from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.teaching import TeachingSession as TeachingSessionModel, TeachingTurn as TeachingTurnModel, DraftVersion as DraftVersionModel, Checkpoint as CheckpointModel
from app.services.retrieval import TfidfRetriever
from app.services.enhanced_retrieval import enhanced_retriever
import os
from app.main import multi_agent_engine


router = APIRouter(prefix="/api/v1/learning/sessions", tags=["learning-sessions"])


Role = Literal["questioner", "explainer", "challenger"]
TaskType = Literal["Task 1", "Task 2"]


class StartSessionRequest(BaseModel):
    role: Role = Field(..., description="Teaching role to start the session with")
    task_type: TaskType = Field("Task 2", description="IELTS task type")
    goal: Optional[str] = Field(None, description="Optional learning goal for the session")


class Turn(BaseModel):
    role: Role
    user_input: Optional[str] = None
    agent_output: Optional[str] = None
    created_at: Optional[str] = None


class DraftVersion(BaseModel):
    content: str = ""
    version: int = 0


class Session(BaseModel):
    id: str
    role: Role
    task_type: TaskType
    goal: Optional[str] = None
    status: Literal["active", "completed"] = "active"
    turns: List[Turn] = []
    latest_draft: DraftVersion = DraftVersion()


class StartSessionResponse(BaseModel):
    session: Session
    first_prompt: str


class StepRequest(BaseModel):
    user_input: Optional[str] = None
    draft_delta: Optional[str] = None


class StepResponse(BaseModel):
    turn: Turn
    draft_version: DraftVersion
    next_action: str


# In-memory placeholder store (replace with DB persistence in M2)
_SESSIONS: dict[str, Session] = {}


def _first_prompt_for_role(role: Role) -> str:
    if role == "questioner":
        return (
            "Welcome! I'll guide you with questions and templates.\n"
            "What's your main position on this topic? Use this template: 'While [opposing view], I believe [your position] because [reason 1] and [reason 2].' Now write your thesis statement."
        )
    if role == "explainer":
        return (
            "Welcome! I'll explain rules with examples and practice.\n"
            "Rule: A strong introduction states position clearly. Example: 'While some argue technology isolates people, I believe it strengthens connections through improved communication and economic opportunities.' Now write your introduction using this pattern."
        )
    return (
        "Welcome! I'll challenge you to improve your writing.\n"
        "Your first challenge: Create a detailed outline. For each body paragraph, write one topic sentence + one specific example. Make sure each paragraph supports a different reason for your position."
    )


@router.post("/start", response_model=StartSessionResponse)
async def start_session(payload: StartSessionRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.get("isGuest", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Guests cannot start teaching sessions")

    # Persist session
    db_session = TeachingSessionModel(
        user_id=int(current_user["user_id"]),
        role=payload.role,
        task_type=payload.task_type,
        goal=payload.goal,
        latest_draft_content="",
        latest_draft_version=0,
        status="active"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Build API response model
    api_session = Session(
        id=str(db_session.id),
        role=payload.role,
        task_type=payload.task_type,
        goal=payload.goal,
        status="active",
        turns=[],
        latest_draft=DraftVersion(content="", version=0)
    )

    return StartSessionResponse(session=api_session, first_prompt=_first_prompt_for_role(payload.role))


@router.post("/{session_id}/step", response_model=StepResponse)
async def step_session(session_id: str, payload: StepRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = db.query(TeachingSessionModel).filter(TeachingSessionModel.id == int(session_id)).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Generate the next tutor message
    user_input = payload.user_input or ""
    role = db_session.role

    agent_output: str | None = None

    # Prefer LLM tutor if available
    # Import ai_feedback_generator inside the function to get the current value
    from app.main import ai_feedback_generator
    
    try:
        if ai_feedback_generator and (getattr(ai_feedback_generator, 'openai_client', None) or getattr(ai_feedback_generator, 'anthropic_client', None)):
            # Build enhanced, action-oriented system prompts
            role_style = {
                "questioner": """You are a Socratic IELTS Writing coach who combines questioning with active writing guidance. For each response:
1. Ask one focused question to develop their thinking
2. Provide a specific writing template or example
3. Ask them to apply it immediately
Keep responses under 3 sentences. Always end with a clear writing task.""",
                
                "explainer": """You are an IELTS Writing coach who explains rules with examples and immediate practice. For each response:
1. Explain one writing rule or technique
2. Show a concrete example from IELTS materials
3. Give them a specific writing task to practice it
Keep responses under 3 sentences. Always include a "Now write..." instruction.""",
                
                "challenger": """You are a tough but fair IELTS Writing coach who identifies weaknesses and provides solutions. For each response:
1. Identify a specific weakness in their writing
2. Show them exactly how to improve it with an example
3. Challenge them to rewrite or improve that section
Keep responses under 3 sentences. Always end with a specific improvement task."""
            }[role]

            # Retrieve relevant examples and guidance from enhanced knowledge base
            enhanced_guidance = ""
            try:
                # Get contextual guidance based on current draft and user input
                guidance = enhanced_retriever.generate_contextual_guidance(
                    query=user_input or "IELTS writing guidance",
                    current_draft=context,
                    task_type="task2"
                )
                
                # Add relevant examples if available
                if guidance["relevant_examples"]:
                    example = guidance["relevant_examples"][0]
                    enhanced_guidance = f"\n\nExample: {example['content'][:200]}... (Band {example['band_score']})"
                
                # Add templates if available
                if guidance["templates"]:
                    template = guidance["templates"][0]
                    enhanced_guidance += f"\n\nTemplate: {template}"
                
            except Exception as e:
                enhanced_guidance = ""

            # Provide minimal context (last draft snapshot + latest user input)
            context = (db_session.latest_draft_content or "").strip()
            context = context[-1500:] if context else ""

            # Compose enhanced prompt with writing guidance context
            user_prompt = (
                "Context (latest draft excerpt, may be empty):\n" + (context or "<empty>") +
                "\n\nLearner input (if any this turn):\n" + (user_input or "<none>") +
                "\n\nInstruction: Respond as the " + role + " coach. Your response should:\n" +
                "- " + ("Ask a question + provide a template + ask them to write" if role == "questioner" else 
                       "Explain a rule + show example + give writing task" if role == "explainer" else
                       "Identify weakness + show improvement + challenge rewrite") +
                "\n- Focus on IELTS Task 2 essay structure and band 7+ techniques" +
                "\n- Always end with a specific writing task they must complete" +
                "\n- Do not write the essay for them, but guide them to write it themselves."
            )

            # Call OpenAI first, otherwise Anthropic; keep output short
            if getattr(ai_feedback_generator, 'openai_client', None):
                response = ai_feedback_generator.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": role_style},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=180
                )
                agent_output = (response.choices[0].message.content or "").strip()
            elif getattr(ai_feedback_generator, 'anthropic_client', None):
                response = ai_feedback_generator.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=180,
                    temperature=0.3,
                    messages=[{"role": "user", "content": role_style + "\n\n" + user_prompt}]
                )
                agent_output = (response.content[0].text or "").strip()

            if agent_output:
                # Append enhanced guidance if available
                agent_output = agent_output[:600] + enhanced_guidance
    except Exception as e:
        agent_output = None

    # Fallback to enhanced deterministic prompts when LLM is not available
    if not agent_output:
        # Get enhanced guidance for fallback prompts
        fallback_guidance = ""
        try:
            guidance = enhanced_retriever.generate_contextual_guidance(
                query=user_input or "IELTS writing guidance",
                current_draft=context,
                task_type="task2"
            )
            
            if guidance["relevant_examples"]:
                example = guidance["relevant_examples"][0]
                fallback_guidance = f"\n\nExample: {example['content'][:150]}... (Band {example['band_score']})"
            
            if guidance["templates"]:
                template = guidance["templates"][0]
                fallback_guidance += f"\n\nTemplate: {template}"
                
        except Exception:
            pass
        
        if role == "questioner":
            agent_output = "What's your main argument? Use this template: 'While [opposing view], I believe [position] because [reason 1] and [reason 2].' Now write your thesis statement." + fallback_guidance
        elif role == "explainer":
            agent_output = "Topic sentences need a clear claim first. Example: 'Technology has revolutionized communication.' Now write your Body 1 topic sentence using this pattern." + fallback_guidance
        else:  # challenger
            agent_output = "Your introduction needs more specificity. Rewrite it using this structure: 'In [context], [topic] has [impact]. While [opposing view], I believe [position] because [reasons].'" + fallback_guidance

    # Update draft version if provided
    draft_version = DraftVersion(content=db_session.latest_draft_content or "", version=db_session.latest_draft_version)
    if payload.draft_delta:
        new_content = ((db_session.latest_draft_content or "") + "\n\n" + payload.draft_delta).strip()
        new_version = (db_session.latest_draft_version or 0) + 1
        db.add(DraftVersionModel(session_id=db_session.id, version=new_version, content=new_content))
        db_session.latest_draft_content = new_content
        db_session.latest_draft_version = new_version

    db.add(TeachingTurnModel(session_id=db_session.id, role=role, user_input=user_input, agent_output=agent_output))
    db.commit()

    turn = Turn(role=role, user_input=user_input, agent_output=agent_output)
    return StepResponse(turn=turn, draft_version=DraftVersion(content=db_session.latest_draft_content or "", version=db_session.latest_draft_version or 0), next_action="continue")


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = db.query(TeachingSessionModel).filter(TeachingSessionModel.id == int(session_id)).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Load turns and latest draft snapshot
    turns = [Turn(role=t.role, user_input=t.user_input, agent_output=t.agent_output, created_at=t.created_at.isoformat() if t.created_at else None) for t in db_session.turns]
    api_session = Session(
        id=str(db_session.id),
        role=db_session.role, task_type=db_session.task_type, goal=db_session.goal,
        status=db_session.status, turns=turns,
        latest_draft=DraftVersion(content=db_session.latest_draft_content or "", version=db_session.latest_draft_version or 0)
    )
    return api_session


class ListSessionsResponse(BaseModel):
    sessions: List[Session]


@router.get("/", response_model=ListSessionsResponse)
async def list_sessions(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(TeachingSessionModel).filter(TeachingSessionModel.user_id == int(current_user["user_id"]))\
        .order_by(TeachingSessionModel.created_at.desc()).all()
    sessions: List[Session] = []
    for r in rows:
        sessions.append(Session(
            id=str(r.id), role=r.role, task_type=r.task_type, goal=r.goal, status=r.status,
            turns=[], latest_draft=DraftVersion(content=r.latest_draft_content or "", version=r.latest_draft_version or 0)
        ))
    return ListSessionsResponse(sessions=sessions)


class DraftsResponse(BaseModel):
    drafts: List[DraftVersion]


@router.get("/{session_id}/drafts", response_model=DraftsResponse)
async def list_drafts(session_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = db.query(TeachingSessionModel).filter(TeachingSessionModel.id == int(session_id)).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    drafts = [DraftVersion(content=d.content, version=d.version) for d in db_session.drafts]
    drafts.sort(key=lambda d: d.version)
    return DraftsResponse(drafts=drafts)


class CheckpointResponse(BaseModel):
    scores: dict
    overall_band_score: float
    assessment_method: str
    diff: str | None = None


@router.post("/{session_id}/checkpoint", response_model=CheckpointResponse)
async def checkpoint(session_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_session = db.query(TeachingSessionModel).filter(TeachingSessionModel.id == int(session_id)).first()
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    draft = (db_session.latest_draft_content or "").strip()
    if not draft:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No draft content to assess")
    result = None
    if multi_agent_engine:
        try:
            # Use existing scoring engine; prompt optional
            result = multi_agent_engine.score_essay("", draft, db_session.task_type)
        except Exception:
            result = None
    if result is None:
        # Offline deterministic fallback (heuristic): use length and simple features
        wc = len(draft.split())
        sentences = max(1, draft.count('.') + draft.count('!') + draft.count('?'))
        avg_sentence_len = wc / sentences
        # naive scores bounded [5,7.5]
        def clamp(x):
            return max(5.0, min(7.5, x))
        scores = {
            "task_achievement": clamp(5.0 + (1.5 if wc > 200 else 0.7 if wc > 120 else 0.0)),
            "coherence_cohesion": clamp(5.0 + (1.2 if avg_sentence_len >= 12 else 0.6)),
            "lexical_resource": clamp(5.0 + (1.0 if len(set(draft.lower().split()))/max(1,wc) > 0.5 else 0.5)),
            "grammatical_range": clamp(5.0 + (1.0 if sentences >= 5 else 0.4)),
        }
        scores["overall_band_score"] = round(sum(scores.values())/4, 1)
        result = {"scores": scores, "assessment_method": "offline_fallback"}
    scores = result.get("scores", {})

    # Persist checkpoint
    cp = CheckpointModel(session_id=db_session.id, draft_version=db_session.latest_draft_version or 0, scores=scores)
    db.add(cp)
    db.commit()

    # Compute simple diff against previous draft version
    prev = None
    if (db_session.latest_draft_version or 0) > 0:
        prev_ver = max(0, (db_session.latest_draft_version or 1) - 1)
        prev_row = db.query(DraftVersionModel).filter(DraftVersionModel.session_id == db_session.id, DraftVersionModel.version == prev_ver).first()
        prev = prev_row.content if prev_row else None
    diff_text = None
    try:
        if prev is not None:
            import difflib
            diff = difflib.unified_diff((prev or '').splitlines(), (draft or '').splitlines(), lineterm='')
            # Keep short diff
            diff_text = "\n".join(list(diff)[:80])
    except Exception:
        diff_text = None

    return CheckpointResponse(
        scores=scores,
        overall_band_score=scores.get("overall_band_score", 0.0),
        assessment_method=result.get("assessment_method", "multi_agent"),
        diff=diff_text
    )



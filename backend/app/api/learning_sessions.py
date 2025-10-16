from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from app.core.security import get_current_user
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.teaching import TeachingSession as TeachingSessionModel, TeachingTurn as TeachingTurnModel, DraftVersion as DraftVersionModel, Checkpoint as CheckpointModel
from app.services.retrieval import TfidfRetriever
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
            "Socratic Guidance — Keep answers brief.\n"
            "1) What is your main position on the topic?\n"
            "2) Draft ONE thesis sentence (no more than 25 words)."
        )
    if role == "explainer":
        return (
            "Explainer — Band 7 intro guidance.\n"
            "Rule: State a clear position. Template: 'While X, I believe Y because A and B.'\n"
            "Task: Try drafting your introduction (2–3 sentences)."
        )
    return (
        "Challenger — Small challenge.\n"
        "Task: Create an outline with 2 body paragraphs. For each: write a topic sentence + one concrete example."
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

    # Very conservative placeholder behavior for M1 skeleton
    user_input = payload.user_input or ""
    role = db_session.role
    # Guardrails: short outputs (<= 2 sentences), actionable next step
    if role == "questioner":
        agent_output = (
            "Great. Next: Write ONE topic sentence for Body 1 that directly supports your thesis."
        )
    elif role == "explainer":
        # Try retrieval to add a citation
        agent_output = "Tip: A topic sentence states a claim first, then you add evidence. Now write one clear topic sentence for Body 1."
        try:
            index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'retrieval_index.json'))
            retriever = TfidfRetriever()
            if os.path.exists(index_path):
                retriever.load(index_path)
                hits = retriever.search("IELTS Task 2 topic sentence guidance", k=1)
                if hits:
                    h = hits[0]
                    agent_output += f"\nSource: {os.path.basename(h.source)} p.{h.page}"
        except Exception:
            pass
    else:  # challenger
        agent_output = (
            "Challenge: Rewrite your introduction to state position in the first sentence and preview two reasons."
        )

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



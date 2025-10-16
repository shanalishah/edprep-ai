from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from app.core.security import get_current_user


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
        return "What is your main position on the topic? Write one clear thesis sentence."
    if role == "explainer":
        return "A band 7 introduction states a clear position. Example: 'While X, I believe Y because A and B.' Try drafting yours."
    return "Challenge: Draft an outline with 2 body paragraphs, each with a topic sentence and one example."


@router.post("/start", response_model=StartSessionResponse)
async def start_session(payload: StartSessionRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("isGuest", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Guests cannot start teaching sessions")

    session_id = f"sess_{current_user['user_id']}_{len(_SESSIONS) + 1}"
    session = Session(
        id=session_id,
        role=payload.role,
        task_type=payload.task_type,
        goal=payload.goal,
        turns=[],
        latest_draft=DraftVersion(content="", version=0)
    )
    _SESSIONS[session_id] = session

    return StartSessionResponse(session=session, first_prompt=_first_prompt_for_role(payload.role))


@router.post("/{session_id}/step", response_model=StepResponse)
async def step_session(session_id: str, payload: StepRequest, current_user: dict = Depends(get_current_user)):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Very conservative placeholder behavior for M1 skeleton
    user_input = payload.user_input or ""
    if session.role == "questioner":
        agent_output = "Thanks. Now, write a topic sentence for your first body paragraph that supports your thesis."
    elif session.role == "explainer":
        agent_output = "Good. Ensure your topic sentence states a clear claim; then add one concrete example."
    else:
        agent_output = "Revise your introduction to clearly state your position and preview two supporting points."

    # Update draft version if provided
    draft_version = session.latest_draft
    if payload.draft_delta:
        new_content = (draft_version.content + "\n\n" + payload.draft_delta).strip()
        draft_version = DraftVersion(content=new_content, version=draft_version.version + 1)
        session.latest_draft = draft_version

    turn = Turn(role=session.role, user_input=user_input, agent_output=agent_output)
    session.turns = session.turns + [turn]

    _SESSIONS[session_id] = session

    return StepResponse(turn=turn, draft_version=draft_version, next_action="continue")


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session



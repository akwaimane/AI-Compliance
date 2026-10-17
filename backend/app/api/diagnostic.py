"""Diagnostic Flash endpoints (Module 1 — AI Risk Categorization Engine).

All endpoints are stateless: answers travel with each request and nothing is
persisted (Zero-Data Retention).
"""

import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..diagnostic import questionnaire
from ..diagnostic.engine import assess
from ..diagnostic.models import (
    Answers,
    AssessmentRequest,
    AssessmentResult,
    NextQuestionRequest,
    NextQuestionResponse,
    Question,
)
from ..reports.pdf import render_report

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])


def _validate(answers: Answers, require_complete: bool = False) -> None:
    try:
        questionnaire.validate_answers(answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if require_complete and questionnaire.next_question(answers) is not None:
        raise HTTPException(status_code=422, detail="Le questionnaire n'est pas terminé.")


@router.get("/questionnaire", response_model=list[Question])
def list_questions() -> list[Question]:
    return questionnaire.QUESTIONS


@router.post("/next", response_model=NextQuestionResponse)
def next_question(request: NextQuestionRequest) -> NextQuestionResponse:
    _validate(request.answers)
    question = questionnaire.next_question(request.answers)
    answered, progress = questionnaire.progress(request.answers)
    return NextQuestionResponse(done=question is None, question=question, answered=answered, progress=progress)


@router.post("/assess", response_model=AssessmentResult)
def assess_system(request: AssessmentRequest) -> AssessmentResult:
    _validate(request.answers, require_complete=True)
    return assess(request.answers)


@router.post("/report", response_class=Response, responses={200: {"content": {"application/pdf": {}}}})
def download_report(request: AssessmentRequest) -> Response:
    _validate(request.answers, require_complete=True)
    result = assess(request.answers)
    pdf = render_report(request.profile, request.answers, result)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", request.profile.system_name).strip("-").lower() or "systeme"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="diagnostic-ai-act-{slug}.pdf"'},
    )

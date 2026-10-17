"""Pydantic models shared by the diagnostic engine, the API and the PDF report."""

from __future__ import annotations

from enum import Enum
from typing import Union

from pydantic import BaseModel, Field

# An answer is a boolean (yes/no), a single option id, or a list of option ids.
AnswerValue = Union[bool, str, list[str]]
Answers = dict[str, AnswerValue]


class QuestionType(str, Enum):
    BOOLEAN = "boolean"
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"


class Option(BaseModel):
    id: str
    label: str
    help: str | None = None
    # In a multi-choice question, an exclusive option ("none of these")
    # cannot be combined with other options.
    exclusive: bool = False


class Question(BaseModel):
    id: str
    section: str
    text: str
    help: str | None = None
    type: QuestionType
    options: list[Option] = Field(default_factory=list)
    legal_reference: str | None = None


class RiskCategory(str, Enum):
    OUT_OF_SCOPE = "out_of_scope"
    MINIMAL = "minimal"
    TRANSPARENCY = "transparency"
    HIGH = "high"
    UNACCEPTABLE = "unacceptable"


class Finding(BaseModel):
    """A rule of the decision tree that fired, with its legal basis."""

    code: str
    title: str
    detail: str
    legal_reference: str


class Obligation(BaseModel):
    code: str
    title: str
    description: str
    legal_reference: str
    applies_from: str
    iso42001_controls: list[str] = Field(default_factory=list)


class ScoreFactor(BaseModel):
    label: str
    points: float


class SystemProfile(BaseModel):
    system_name: str = Field(min_length=1, max_length=200)
    organization: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    contact_email: str | None = Field(default=None, max_length=254)


class AssessmentRequest(BaseModel):
    profile: SystemProfile
    answers: Answers


class AssessmentResult(BaseModel):
    category: RiskCategory
    category_label: str
    risk_score: int = Field(ge=0, le=100)
    score_factors: list[ScoreFactor]
    summary: str
    findings: list[Finding]
    obligations: list[Obligation]
    flags: list[str]
    max_penalty: str | None


class NextQuestionRequest(BaseModel):
    answers: Answers = Field(default_factory=dict)


class NextQuestionResponse(BaseModel):
    done: bool
    question: Question | None = None
    answered: int
    # Estimated share of the questionnaire completed, from 0 to 1.
    progress: float

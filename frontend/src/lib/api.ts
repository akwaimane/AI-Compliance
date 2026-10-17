// Typed client for the FastAPI backend (Diagnostic Flash endpoints).

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type AnswerValue = boolean | string | string[];
export type Answers = Record<string, AnswerValue>;

export type QuestionType = "boolean" | "single_choice" | "multi_choice";

export interface Option {
  id: string;
  label: string;
  help: string | null;
  exclusive: boolean;
}

export interface Question {
  id: string;
  section: string;
  text: string;
  help: string | null;
  type: QuestionType;
  options: Option[];
  legal_reference: string | null;
}

export interface NextQuestionResponse {
  done: boolean;
  question: Question | null;
  answered: number;
  progress: number;
}

export type RiskCategory = "out_of_scope" | "minimal" | "transparency" | "high" | "unacceptable";

export interface Finding {
  code: string;
  title: string;
  detail: string;
  legal_reference: string;
}

export interface Obligation {
  code: string;
  title: string;
  description: string;
  legal_reference: string;
  applies_from: string;
  iso42001_controls: string[];
}

export interface AssessmentResult {
  category: RiskCategory;
  category_label: string;
  risk_score: number;
  score_factors: { label: string; points: number }[];
  summary: string;
  findings: Finding[];
  obligations: Obligation[];
  flags: string[];
  max_penalty: string | null;
}

export interface SystemProfile {
  system_name: string;
  organization?: string;
  description?: string;
  contact_email?: string;
}

async function post(path: string, body: unknown): Promise<Response> {
  const response = await fetch(`${API_URL}/api/v1${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    let message = `Erreur ${response.status}`;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch {
      // Keep the generic message when the body is not JSON.
    }
    throw new Error(message);
  }
  return response;
}

export async function fetchNextQuestion(answers: Answers): Promise<NextQuestionResponse> {
  return (await post("/diagnostic/next", { answers })).json();
}

export async function assessSystem(profile: SystemProfile, answers: Answers): Promise<AssessmentResult> {
  return (await post("/diagnostic/assess", { profile, answers })).json();
}

export async function downloadReport(profile: SystemProfile, answers: Answers): Promise<void> {
  const response = await post("/diagnostic/report", { profile, answers });
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const filename = /filename="([^"]+)"/.exec(disposition)?.[1] ?? "diagnostic-ai-act.pdf";
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

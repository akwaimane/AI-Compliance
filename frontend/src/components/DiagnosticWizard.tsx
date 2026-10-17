"use client";

import { useState } from "react";

import QuestionCard from "@/components/QuestionCard";
import ResultView from "@/components/ResultView";
import {
  assessSystem,
  downloadReport,
  fetchNextQuestion,
  type AnswerValue,
  type Answers,
  type AssessmentResult,
  type Question,
  type SystemProfile,
} from "@/lib/api";

type Step = "profile" | "questions" | "result";

interface HistoryEntry {
  question: Question;
  progress: number;
}

export default function DiagnosticWizard() {
  const [step, setStep] = useState<Step>("profile");
  const [profile, setProfile] = useState<SystemProfile>({ system_name: "" });
  const [answers, setAnswers] = useState<Answers>({});
  // Questions answered so far, in order, so the user can go back.
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [current, setCurrent] = useState<HistoryEntry | null>(null);
  const [draft, setDraft] = useState<AnswerValue | undefined>(undefined);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Une erreur inattendue est survenue.");
    } finally {
      setBusy(false);
    }
  }

  async function advance(nextAnswers: Answers) {
    const next = await fetchNextQuestion(nextAnswers);
    if (next.done || !next.question) {
      setResult(await assessSystem(profile, nextAnswers));
      setCurrent(null);
      setStep("result");
    } else {
      setCurrent({ question: next.question, progress: next.progress });
      setStep("questions");
    }
  }

  function start() {
    run(() => advance({}));
  }

  function answer(value: AnswerValue) {
    if (!current) return;
    const nextAnswers = { ...answers, [current.question.id]: value };
    run(async () => {
      await advance(nextAnswers);
      setAnswers(nextAnswers);
      setHistory((h) => [...h, current]);
      setDraft(undefined);
    });
  }

  function back() {
    const previous = history.at(-1);
    if (!previous) {
      setStep("profile");
      return;
    }
    const { [previous.question.id]: previousValue, ...rest } = answers;
    setAnswers(rest);
    setHistory(history.slice(0, -1));
    setDraft(previousValue);
    setCurrent(previous);
    setStep("questions");
  }

  function restart() {
    setStep("profile");
    setAnswers({});
    setHistory([]);
    setCurrent(null);
    setDraft(undefined);
    setResult(null);
    setError(null);
  }

  function cleanProfile(): SystemProfile {
    return {
      system_name: profile.system_name.trim(),
      organization: profile.organization?.trim() || undefined,
      description: profile.description?.trim() || undefined,
      contact_email: profile.contact_email?.trim() || undefined,
    };
  }

  return (
    <div className="mx-auto w-full max-w-2xl">
      {step === "questions" && current && (
        <div className="mb-6">
          <div className="mb-1 flex justify-between text-xs text-slate-500">
            <span>Question {history.length + 1}</span>
            <span>{Math.round(current.progress * 100)} %</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
            <div className="h-full rounded-full bg-teal-600 transition-all" style={{ width: `${current.progress * 100}%` }} />
          </div>
        </div>
      )}

      {error && (
        <div role="alert" className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      )}

      {step === "profile" && (
        <form
          className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          onSubmit={(event) => {
            event.preventDefault();
            setProfile(cleanProfile());
            start();
          }}
        >
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Identifiez le système d&apos;IA à évaluer</h2>
            <p className="mt-1 text-sm text-slate-600">Ces informations figurent uniquement dans votre rapport PDF. Rien n&apos;est conservé.</p>
          </div>
          <Field label="Nom du système *">
            <input
              required
              maxLength={200}
              value={profile.system_name}
              onChange={(e) => setProfile({ ...profile, system_name: e.target.value })}
              placeholder="Ex. : TalentMatch — présélection de CV"
              className={inputClass}
            />
          </Field>
          <Field label="Organisation">
            <input maxLength={200} value={profile.organization ?? ""} onChange={(e) => setProfile({ ...profile, organization: e.target.value })} className={inputClass} />
          </Field>
          <Field label="Description de la finalité">
            <textarea
              maxLength={2000}
              rows={3}
              value={profile.description ?? ""}
              onChange={(e) => setProfile({ ...profile, description: e.target.value })}
              className={inputClass}
            />
          </Field>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={busy || !profile.system_name.trim()}
              className="rounded-lg bg-teal-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-800 disabled:opacity-40"
            >
              {busy ? "Chargement…" : "Commencer le diagnostic"}
            </button>
          </div>
        </form>
      )}

      {step === "questions" && current && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <QuestionCard key={current.question.id} question={current.question} initialValue={draft} onSubmit={answer} onBack={back} busy={busy} />
        </div>
      )}

      {step === "result" && result && (
        <ResultView
          systemName={profile.system_name}
          result={result}
          downloading={busy}
          onDownload={() => run(() => downloadReport(profile, answers))}
          onRestart={restart}
        />
      )}
    </div>
  );
}

const inputClass =
  "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-900 focus:outline-none focus:ring-1 focus:ring-blue-900";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-800">{label}</span>
      {children}
    </label>
  );
}

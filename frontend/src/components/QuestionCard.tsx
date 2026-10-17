"use client";

import { useState } from "react";

import type { AnswerValue, Question } from "@/lib/api";

interface Props {
  question: Question;
  initialValue?: AnswerValue;
  onSubmit: (value: AnswerValue) => void;
  onBack?: () => void;
  busy: boolean;
}

export default function QuestionCard({ question, initialValue, onSubmit, onBack, busy }: Props) {
  const [value, setValue] = useState<AnswerValue | undefined>(initialValue);

  const selectedList = Array.isArray(value) ? value : [];
  const canSubmit =
    question.type === "multi_choice" ? selectedList.length > 0 : value !== undefined;

  function toggle(optionId: string, exclusive: boolean) {
    if (selectedList.includes(optionId)) {
      setValue(selectedList.filter((id) => id !== optionId));
      return;
    }
    const exclusiveIds = question.options.filter((o) => o.exclusive).map((o) => o.id);
    setValue(exclusive ? [optionId] : [...selectedList.filter((id) => !exclusiveIds.includes(id)), optionId]);
  }

  return (
    <form
      className="space-y-6"
      onSubmit={(event) => {
        event.preventDefault();
        if (canSubmit && value !== undefined) onSubmit(value);
      }}
    >
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-teal-700">
          {question.section}
          {question.legal_reference && <span className="ml-2 font-normal normal-case text-slate-500">· {question.legal_reference}</span>}
        </p>
        <h2 className="mt-2 text-xl font-semibold text-slate-900">{question.text}</h2>
        {question.help && <p className="mt-2 text-sm text-slate-600">{question.help}</p>}
      </div>

      {question.type === "boolean" ? (
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Oui", v: true },
            { label: "Non", v: false },
          ].map(({ label, v }) => (
            <button
              key={label}
              type="button"
              onClick={() => setValue(v)}
              className={`rounded-lg border px-4 py-3 text-sm font-medium transition ${
                value === v ? "border-blue-900 bg-blue-900 text-white" : "border-slate-300 bg-white text-slate-800 hover:border-blue-900"
              }`}
              aria-pressed={value === v}
            >
              {label}
            </button>
          ))}
        </div>
      ) : (
        <fieldset className="space-y-2">
          <legend className="sr-only">{question.text}</legend>
          {question.options.map((option) => {
            const multi = question.type === "multi_choice";
            const checked = multi ? selectedList.includes(option.id) : value === option.id;
            return (
              <label
                key={option.id}
                className={`flex cursor-pointer gap-3 rounded-lg border px-4 py-3 transition ${
                  checked ? "border-blue-900 bg-blue-50" : "border-slate-300 bg-white hover:border-blue-900"
                }`}
              >
                <input
                  type={multi ? "checkbox" : "radio"}
                  name={question.id}
                  className="mt-1 accent-blue-900"
                  checked={checked}
                  onChange={() => (multi ? toggle(option.id, option.exclusive) : setValue(option.id))}
                />
                <span>
                  <span className="block text-sm font-medium text-slate-900">{option.label}</span>
                  {option.help && <span className="block text-xs text-slate-600">{option.help}</span>}
                </span>
              </label>
            );
          })}
        </fieldset>
      )}

      <div className="flex items-center justify-between">
        {onBack ? (
          <button type="button" onClick={onBack} disabled={busy} className="text-sm font-medium text-slate-600 hover:text-slate-900 disabled:opacity-50">
            ← Précédent
          </button>
        ) : (
          <span />
        )}
        <button
          type="submit"
          disabled={!canSubmit || busy}
          className="rounded-lg bg-teal-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {busy ? "Chargement…" : "Continuer"}
        </button>
      </div>
    </form>
  );
}

"use client";

import Link from "next/link";

import type { AssessmentResult } from "@/lib/api";
import { CATEGORY_STYLES } from "@/lib/risk";

interface Props {
  systemName: string;
  result: AssessmentResult;
  onDownload: () => void;
  downloading: boolean;
  onRestart: () => void;
}

export default function ResultView({ systemName, result, onDownload, downloading, onRestart }: Props) {
  const style = CATEGORY_STYLES[result.category];

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Résultat du diagnostic pour</p>
        <h2 className="text-2xl font-bold text-slate-900">{systemName}</h2>
        <div className="mt-4 flex flex-wrap items-center gap-4">
          <span className={`rounded-full px-4 py-1.5 text-sm font-semibold ring-1 ${style.badge}`}>{result.category_label}</span>
          <span className="text-sm text-slate-600">
            AI Risk Score : <strong className="text-lg text-slate-900">{result.risk_score}</strong> / 100
          </span>
        </div>
        <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-slate-100" role="meter" aria-valuenow={result.risk_score} aria-valuemin={0} aria-valuemax={100} aria-label="AI Risk Score">
          <div className={`h-full rounded-full ${style.bar}`} style={{ width: `${result.risk_score}%` }} />
        </div>
        <p className="mt-4 text-slate-700">{result.summary}</p>
        {result.max_penalty && (
          <p className="mt-2 text-sm text-slate-700">
            <strong>Sanction maximale encourue :</strong> {result.max_penalty}
          </p>
        )}
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={onDownload}
            disabled={downloading}
            className="rounded-lg bg-blue-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-950 disabled:opacity-50"
          >
            {downloading ? "Génération…" : "Télécharger le rapport PDF"}
          </button>
          <button onClick={onRestart} className="rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-800 hover:border-slate-500">
            Nouveau diagnostic
          </button>
        </div>
      </section>

      {result.findings.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-blue-900">Constats de la classification</h3>
          <ul className="space-y-2">
            {result.findings.map((finding) => (
              <li key={finding.code} className="rounded-lg border border-slate-200 bg-white px-4 py-3">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="font-medium text-slate-900">{finding.title}</span>
                  <span className="text-xs text-slate-500">{finding.legal_reference}</span>
                </div>
                <p className="text-sm text-slate-600">{finding.detail}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {result.flags.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-blue-900">Points d&apos;attention</h3>
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {result.flags.map((flag) => (
              <li key={flag}>{flag}</li>
            ))}
          </ul>
        </section>
      )}

      {result.obligations.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-blue-900">Obligations applicables · correspondance ISO/IEC 42001</h3>
          <div className="space-y-3">
            {result.obligations.map((obligation) => (
              <article key={obligation.code} className="rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h4 className="font-semibold text-slate-900">{obligation.title}</h4>
                  <span className="text-xs text-slate-500">
                    {obligation.legal_reference} · applicable dès le {obligation.applies_from}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-600">{obligation.description}</p>
                {obligation.iso42001_controls.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {obligation.iso42001_controls.map((control) => (
                      <span key={control} className="rounded bg-teal-50 px-2 py-0.5 text-xs text-teal-800 ring-1 ring-teal-200">
                        {control}
                      </span>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      {(result.category === "high" || result.category === "transparency") && (
        <section className="rounded-xl bg-blue-900 p-6 text-white">
          <h3 className="text-lg font-semibold">Passez de la classification à la conformité</h3>
          <p className="mt-2 text-sm text-blue-100">
            L&apos;Audit One-Shot AI Act analyse vos jeux de données (biais, explicabilité) et génère le dossier technique de l&apos;annexe IV.
            L&apos;abonnement Enterprise ajoute le SMIA ISO/IEC 42001 et la préparation à la certification.
          </p>
          <Link href="/#offres" className="mt-4 inline-block rounded-lg bg-white px-4 py-2 text-sm font-semibold text-blue-900 hover:bg-blue-50">
            Découvrir les offres
          </Link>
        </section>
      )}

      <p className="text-xs text-slate-500">
        Pré-qualification automatisée fondée sur vos déclarations et sur le texte du règlement (UE) 2024/1689. Ce résultat ne constitue pas un avis
        juridique. Aucune réponse n&apos;est conservée (Zero-Data Retention).
      </p>
    </div>
  );
}

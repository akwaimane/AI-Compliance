import Link from "next/link";

import { CATEGORY_STYLES, RISK_LEVELS } from "@/lib/risk";

const PILLARS = [
  {
    title: "Pilier 1 · AI Act",
    items: [
      "Diagnostic Flash et classification du risque",
      "Audit algorithmique des jeux de données (biais, explicabilité)",
      "Dossier technique de l'annexe IV et déclaration UE de conformité",
    ],
  },
  {
    title: "Pilier 2 · ISO/IEC 42001 (SMIA)",
    items: [
      "Politique d'IA, parties prenantes, rôles et responsabilités",
      "Évaluation des risques et contrôles de l'annexe A",
      "Actions correctives (CAPA) et espace auditeur de certification",
    ],
  },
];

const OFFERS = [
  { name: "Diagnostic Flash", price: "Gratuit", description: "Classification du risque AI Act, AI Risk Score et rapport PDF.", cta: true },
  { name: "Audit One-Shot AI Act", price: "5 000 € à 15 000 € / système", description: "Audit d'un système à haut risque et génération du dossier technique réglementaire." },
  { name: "Enterprise SaaS", price: "1 500 € à 3 500 € / mois", description: "Gouvernance unifiée AI Act + ISO/IEC 42001, suivi continu et préparation à la certification." },
];

export default function Home() {
  return (
    <div>
      <section className="bg-gradient-to-b from-white to-slate-50 px-4 py-20">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">Double conformité AI Act & ISO/IEC 42001</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-blue-900 sm:text-5xl">Votre système d&apos;IA est-il conforme à l&apos;AI Act ?</h1>
          <p className="mt-5 text-lg text-slate-600">
            Classez vos systèmes d&apos;IA en quelques minutes, identifiez vos obligations réglementaires et leur correspondance avec la norme ISO/IEC
            42001.
          </p>
          <Link href="/diagnostic" className="mt-8 inline-block rounded-lg bg-teal-700 px-6 py-3 font-semibold text-white hover:bg-teal-800">
            Lancer le Diagnostic Flash gratuit
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-14">
        <h2 className="text-2xl font-bold text-blue-900">Quatre niveaux de risque</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {RISK_LEVELS.map((level) => (
            <div key={level.category} className="rounded-xl border border-slate-200 bg-white p-5">
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ring-1 ${CATEGORY_STYLES[level.category].badge}`}>{level.label}</span>
              <p className="mt-3 text-sm text-slate-600">{level.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-14">
        <h2 className="text-2xl font-bold text-blue-900">Une plateforme, deux piliers</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {PILLARS.map((pillar) => (
            <div key={pillar.title} className="rounded-xl border border-slate-200 bg-white p-6">
              <h3 className="font-semibold text-teal-700">{pillar.title}</h3>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
                {pillar.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section id="offres" className="mx-auto max-w-6xl px-4 py-14">
        <h2 className="text-2xl font-bold text-blue-900">Offres</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {OFFERS.map((offer) => (
            <div key={offer.name} className="flex flex-col rounded-xl border border-slate-200 bg-white p-6">
              <h3 className="font-semibold text-slate-900">{offer.name}</h3>
              <p className="mt-1 text-lg font-bold text-blue-900">{offer.price}</p>
              <p className="mt-3 flex-1 text-sm text-slate-600">{offer.description}</p>
              {offer.cta && (
                <Link href="/diagnostic" className="mt-4 rounded-lg bg-teal-700 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-teal-800">
                  Commencer
                </Link>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

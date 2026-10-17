import type { RiskCategory } from "./api";

export const CATEGORY_STYLES: Record<RiskCategory, { badge: string; bar: string }> = {
  out_of_scope: { badge: "bg-slate-100 text-slate-700 ring-slate-300", bar: "bg-slate-400" },
  minimal: { badge: "bg-green-50 text-green-800 ring-green-300", bar: "bg-green-600" },
  transparency: { badge: "bg-amber-50 text-amber-800 ring-amber-300", bar: "bg-amber-500" },
  high: { badge: "bg-orange-50 text-orange-800 ring-orange-300", bar: "bg-orange-600" },
  unacceptable: { badge: "bg-red-50 text-red-800 ring-red-300", bar: "bg-red-700" },
};

export const RISK_LEVELS: { category: RiskCategory; label: string; description: string }[] = [
  { category: "unacceptable", label: "Risque inacceptable", description: "Pratiques interdites (art. 5) : notation sociale, manipulation, reconnaissance des émotions au travail…" },
  { category: "high", label: "Haut risque", description: "Recrutement, crédit, éducation, infrastructures critiques, produits réglementés (art. 6, annexes I et III)." },
  { category: "transparency", label: "Risque limité", description: "Chatbots, contenus générés, hypertrucages : obligations de transparence (art. 50)." },
  { category: "minimal", label: "Risque minimal", description: "Filtres anti-spam, recommandations simples : maîtrise de l'IA et codes de conduite volontaires." },
];

import type { Metadata } from "next";

import DiagnosticWizard from "@/components/DiagnosticWizard";

export const metadata: Metadata = {
  title: "Diagnostic Flash AI Act — AI Compliance",
};

export default function DiagnosticPage() {
  return (
    <div className="px-4 py-10">
      <div className="mx-auto mb-8 max-w-2xl">
        <h1 className="text-3xl font-bold text-blue-900">Diagnostic Flash AI Act</h1>
        <p className="mt-2 text-slate-600">
          Classez votre système d&apos;IA selon le règlement (UE) 2024/1689 en quelques minutes et obtenez votre AI Risk Score, vos obligations et
          leur correspondance ISO/IEC 42001.
        </p>
      </div>
      <DiagnosticWizard />
    </div>
  );
}

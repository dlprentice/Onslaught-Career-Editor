import { CheckCircle2, LockKeyhole, PackageCheck, SearchCheck } from "lucide-react";
import { DetailGrid, DetailTile, MetricCard, PageIntro, PageSection } from "@/components/common/ProductPrimitives";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { ReleasePolicySummary, RuntimeSnapshot, Tone } from "@/types/onslaught-api";

interface ReleaseSectionProps {
  releasePolicy: ReleasePolicySummary | null;
  releaseGates: RuntimeSnapshot["releaseGates"];
  releaseBusy: boolean;
  releaseError: string | null;
  onRefreshReleasePolicy: () => void | Promise<void>;
}

export function ReleaseSection({
  releasePolicy,
  releaseGates,
  releaseBusy,
  releaseError,
  onRefreshReleasePolicy
}: ReleaseSectionProps) {
  const passingGates = releaseGates.filter((gate) => gate.status.toLowerCase().includes("pass")).length;

  return (
    <PageSection testId="section-release">
      <PageIntro
        eyebrow="Release"
        title="Review public readiness without leaking private evidence"
        body="Release shows what passed, what stays private, and what proof is still needed before a public package."
        action={
          <Button variant="secondary" onClick={() => void onRefreshReleasePolicy()} disabled={releaseBusy}>
            <SearchCheck className="h-4 w-4" aria-hidden="true" />
            {releaseBusy ? "Checking..." : "Refresh policy"}
          </Button>
        }
      />

      {releaseError ? <div className="rounded-lg border border-[#fecdca] bg-[#fef3f2] p-4 text-sm text-[#b42318]">{releaseError}</div> : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <main className="grid gap-5">
          <Card>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricCard label="Release posture" value="Public-safe candidate" detail="Source and docs are curated for release review." tone="good" />
              <MetricCard label="Private evidence" value="Excluded" detail="Runtime screenshots, proof JSON, and local assets stay out." tone="good" />
              <MetricCard label="Bundle smoke" value="Passed" detail="Automated smoke is part of release signoff." tone="good" />
              <MetricCard label="Next proof" value="Packaged runtime" detail="Portable bundle runtime clicks still need proof." tone="warn" />
            </div>
          </Card>

          <Card data-testid="release-gates">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Automated gates</h3>
                <p className="mt-1 text-sm text-workbench-muted">Build, smoke, policy, and docs checks that protect the public package.</p>
              </div>
              <StatusPill tone="good">{passingGates || releaseGates.length} tracked</StatusPill>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {releaseGates.map((gate) => (
                <div key={gate.label} className="rounded-lg border border-workbench-border bg-workbench-panel2 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-workbench-text">{gate.label}</p>
                      <p className="mt-1 text-sm leading-6 text-workbench-muted">{gate.detail}</p>
                    </div>
                    <StatusPill tone={gateTone(gate.status)}>{gate.status}</StatusPill>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card data-testid="release-scope">
            <div className="mb-4 flex items-center gap-3">
              <LockKeyhole className="h-6 w-6 text-[#2457c5]" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Public and private scope</h3>
                <p className="text-sm text-workbench-muted">Public releases include app source and safe docs, not private local runtime evidence.</p>
              </div>
            </div>
            {releasePolicy ? (
              <div className="grid gap-3 md:grid-cols-4">
                <MetricCard label="Community docs" value={releasePolicy.counts.communityDocs} tone="good" />
                <MetricCard label="Maintainer docs" value={releasePolicy.counts.maintainerDocs} tone="warn" />
                <MetricCard label="Public allow" value={releasePolicy.counts.allow} tone="good" />
                <MetricCard label="Excluded/private" value={releasePolicy.counts.deny} tone="warn" />
              </div>
            ) : (
              <p className="text-sm text-workbench-muted">Release policy is loading.</p>
            )}
            <DetailsDisclosure className="mt-4" title="Manifest and path rules" summary="Show release accounting">
              <DetailGrid>
                {releasePolicy?.profiles.map((profile) => (
                  <DetailTile key={profile.id} label={profile.title} value={profile.status} detail={profile.summary} />
                ))}
              </DetailGrid>
              <div className="mt-3 grid gap-2 text-xs text-workbench-muted">
                {releasePolicy?.pathRules.slice(0, 16).map((rule) => (
                  <p key={`${rule.classification}-${rule.relativePath}`}>
                    {rule.label}: {rule.classification} ({rule.exists ? "present" : "not present"})
                  </p>
                ))}
              </div>
            </DetailsDisclosure>
          </Card>
        </main>

        <aside className="grid gap-4 self-start">
          <Card>
            <PackageCheck className="h-8 w-8 text-[#2457c5]" aria-hidden="true" />
            <h3 className="mt-3 text-lg font-semibold text-workbench-text">Next recommended action</h3>
            <p className="mt-2 text-sm leading-6 text-workbench-muted">
              Prove packaged portable-bundle media playback and Game Harness behavior before cutting a signed or installer-grade public release.
            </p>
          </Card>

          <Card data-testid="release-evidence-reports">
            <h3 className="text-lg font-semibold text-workbench-text">Evidence reports</h3>
            <div className="mt-4 grid gap-3">
              {[
                "release_candidate_evidence_2026-04-30.md",
                "ux_goal_evidence_2026-05-01.md",
                "Private runtime evidence excluded"
              ].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-lg border border-workbench-border bg-workbench-panel2 p-3">
                  <CheckCircle2 className="h-5 w-5 text-[#16a34a]" aria-hidden="true" />
                  <p className="text-sm font-medium text-workbench-text">{item}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold text-workbench-text">Not proven yet</h3>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-workbench-muted">
              <li>Signed installer-grade release.</li>
              <li>Packaged portable-bundle runtime media playback.</li>
              <li>Packaged portable-bundle Game Harness behavior.</li>
              <li>Continuous frame streaming and open-ended autonomy.</li>
            </ul>
          </Card>
        </aside>
      </div>
    </PageSection>
  );
}

function gateTone(status: string): Tone {
  const value = status.toLowerCase();
  if (value.includes("pass") || value.includes("green")) return "good";
  if (value.includes("fail") || value.includes("block")) return "danger";
  return "warn";
}

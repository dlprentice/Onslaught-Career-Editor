import { useState } from "react";
import { Camera, CheckCircle2, Eye, Gamepad2, HardDrive, Play, RotateCcw, ShieldCheck, Square, Target } from "lucide-react";
import { DetailGrid, DetailTile, EmptyState, MetricCard, PageIntro, PageSection, StepCard } from "@/components/common/ProductPrimitives";
import { fileNameFromPath, safeSummary } from "@/components/common/format";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { LucideIcon } from "lucide-react";
import type { GameHarnessProfileSummary, Tone, WorkbenchJobDefinition, WorkbenchJobRunSummary } from "@/types/onslaught-api";

interface GameHarnessSectionProps {
  gameHarnessProfile: GameHarnessProfileSummary | null;
  gameFolderPath: string;
  gameFolderBusy: boolean;
  gameFolderError: string | null;
  safeProfileBusy: boolean;
  safeProfileError: string | null;
  safeProfileRun: WorkbenchJobRunSummary | null;
  copiedExecutablePath: string;
  patchWorkflowRun: WorkbenchJobRunSummary | null;
  patchWorkflowBusy: string | null;
  patchWorkflowError: string | null;
  launchProfileJob: WorkbenchJobDefinition | null;
  stopManagedProcessJob: WorkbenchJobDefinition | null;
  launchProfileBusy: boolean;
  stopManagedProcessBusy: boolean;
  capturePlanJob: WorkbenchJobDefinition | null;
  frameCaptureJob: WorkbenchJobDefinition | null;
  frameSequenceJob: WorkbenchJobDefinition | null;
  inputPlanJob: WorkbenchJobDefinition | null;
  inputSendJob: WorkbenchJobDefinition | null;
  launchProfileRun: WorkbenchJobRunSummary | null;
  stopManagedProcessRun: WorkbenchJobRunSummary | null;
  capturePlanRun: WorkbenchJobRunSummary | null;
  frameCaptureRun: WorkbenchJobRunSummary | null;
  frameSequenceRun: WorkbenchJobRunSummary | null;
  inputRun: WorkbenchJobRunSummary | null;
  launchJobsArmed: boolean;
  onGameFolderPathChange: (value: string) => void;
  onBrowseGameFolder: () => void | Promise<void>;
  onUseGameFolder: () => void | Promise<void>;
  onResetGameFolder: () => void | Promise<void>;
  onPrepareSafeProfile: () => void | Promise<void>;
  onOpenPatchBenchForWindowedPatch: () => void;
  onRunWindowedPatchWorkflow: (definitionId: "patch.planCatalogPatch" | "patch.applyCatalogPatch") => void | Promise<void>;
  onRunWorkbenchJob: (job: WorkbenchJobDefinition) => void | Promise<void>;
  onLaunchJobsArmedChange: (value: boolean) => void;
}

export function GameHarnessSection({
  gameHarnessProfile,
  gameFolderPath,
  gameFolderBusy,
  gameFolderError,
  safeProfileBusy,
  safeProfileError,
  safeProfileRun,
  copiedExecutablePath,
  patchWorkflowRun,
  patchWorkflowBusy,
  patchWorkflowError,
  launchProfileJob,
  stopManagedProcessJob,
  launchProfileBusy,
  stopManagedProcessBusy,
  capturePlanJob,
  frameCaptureJob,
  frameSequenceJob,
  inputPlanJob,
  inputSendJob,
  launchProfileRun,
  stopManagedProcessRun,
  capturePlanRun,
  frameCaptureRun,
  frameSequenceRun,
  inputRun,
  launchJobsArmed,
  onGameFolderPathChange,
  onBrowseGameFolder,
  onUseGameFolder,
  onResetGameFolder,
  onPrepareSafeProfile,
  onOpenPatchBenchForWindowedPatch,
  onRunWindowedPatchWorkflow,
  onRunWorkbenchJob,
  onLaunchJobsArmedChange
}: GameHarnessSectionProps) {
  const [inputJobsArmed, setInputJobsArmed] = useState(false);
  const profileReady = Boolean(gameHarnessProfile?.ready || safeProfileRun?.status === "completed");
  const windowedPatchReady = patchWorkflowRun?.status === "completed" || Boolean(copiedExecutablePath);
  const launchToolAvailable = launchProfileJob?.status === "available";
  const launchRunning = launchProfileBusy;
  const launchCompleted = launchProfileRun?.status === "completed";
  const launchFailed = launchProfileRun?.status === "failed" || launchProfileRun?.status === "cancelled";
  const launchPrerequisitesReady = profileReady && windowedPatchReady && launchToolAvailable;
  const launchStatusLabel = launchRunning ? "Running" : launchCompleted ? "Completed" : launchPrerequisitesReady ? "Ready" : "Not ready";
  const launchStatusTone: Tone = launchRunning ? "warn" : launchCompleted ? "good" : launchFailed ? "danger" : launchPrerequisitesReady ? "good" : "warn";
  const launchReadinessText = !profileReady
    ? "Not ready: prepare a copied profile first."
    : !windowedPatchReady
      ? "Not ready: apply the display patch to the copied executable first."
      : !launchToolAvailable
        ? "Not ready: managed launch tool is unavailable."
        : launchRunning
          ? "Managed launch is running against the copied profile."
          : launchCompleted
            ? "Managed launch completed; observe and input steps can use the recorded run."
            : !launchJobsArmed
              ? "Ready: confirm copied-profile launch safety to enable the action."
              : "Ready to launch the copied profile with existing safety gates.";
  const launchBlockedReason = !profileReady
    ? "Prepare a copied profile first."
    : !windowedPatchReady
      ? "Apply the display patch to the copied executable first."
      : !launchJobsArmed
        ? "Confirm copied-profile launch safety first."
        : undefined;
  const stopStatusLabel = stopManagedProcessBusy ? "Stopping" : stopManagedProcessRun?.status === "completed" ? "Stopped" : launchProfileRun ? "Ready" : "Pending";
  const stopStatusTone: Tone = stopManagedProcessRun?.status === "completed" ? "good" : launchProfileRun ? "warn" : "neutral";
  const stopBlockedReason = !launchProfileRun
    ? "Launch a managed process before stopping."
    : !launchJobsArmed
      ? "Confirm copied-profile launch safety first."
      : undefined;
  const inputBlockedReason = !launchProfileRun
    ? "Launch a managed game before sending input."
    : !inputJobsArmed
      ? "Confirm exact managed target before sending input."
      : undefined;
  const observed = Boolean(frameCaptureRun || frameSequenceRun);
  const inputPlanned = Boolean(inputRun);

  return (
    <PageSection testId="section-harness">
      <PageIntro
        eyebrow="Game Harness"
        title="Run a bounded game investigation"
        body="Onslaught runs a safe guided loop to explore a specific game area, capture evidence, and help you understand what is happening."
      />

      <div className="grid gap-5 xl:grid-cols-[20rem_minmax(0,1fr)_24rem]">
        <aside className="grid gap-3 self-start">
          <StepCard
            number={1}
            title="Prepare Copied Profile"
            body="Create a safe isolated copy of the game profile and settings."
            active
            status={<StatusPill tone={profileReady ? "good" : "warn"}>{profileReady ? "Ready" : "Needed"}</StatusPill>}
            action={
              <Button onClick={() => void onPrepareSafeProfile()} disabled={safeProfileBusy || gameFolderBusy}>
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                {safeProfileBusy ? "Preparing..." : "Prepare copied profile"}
              </Button>
            }
          />
          <StepCard
            number={2}
            title="Apply Windowed Patch"
            body="Enable reliable window capture on the copied executable only."
            status={<StatusPill tone={windowedPatchReady ? "good" : "warn"}>{windowedPatchReady ? "Copy ready" : "Copy required"}</StatusPill>}
            action={
              <div className="grid gap-2">
                <Button variant="secondary" onClick={onOpenPatchBenchForWindowedPatch}>
                  Open Patch Bench
                </Button>
                <Button onClick={() => void onRunWindowedPatchWorkflow("patch.applyCatalogPatch")} disabled={!copiedExecutablePath || patchWorkflowBusy !== null}>
                  Apply display patch
                </Button>
              </div>
            }
          />
          <StepCard
            number={3}
            title="Launch Managed Game"
            body="Launch only the copied profile as a managed process."
            status={<StatusPill tone={launchStatusTone}>{launchStatusLabel}</StatusPill>}
            action={
              <div data-testid="harness-launch-step" className="grid gap-3">
                <p data-testid="harness-launch-readiness" className="text-sm leading-6 text-workbench-muted">
                  {launchReadinessText}
                </p>
                <label className="flex items-start gap-2 rounded-md border border-workbench-border bg-white p-3 text-sm text-workbench-muted">
                  <input
                    className="mt-1"
                    type="checkbox"
                    checked={launchJobsArmed}
                    onChange={(event) => onLaunchJobsArmedChange(event.target.checked)}
                  />
                  <span>Confirm this will only start the copied profile and use the app safety gates.</span>
                </label>
                <HarnessJobButton
                  job={launchProfileJob}
                  label={launchRunning ? "Launching..." : launchCompleted ? "Launch again" : "Launch managed game"}
                  onRun={onRunWorkbenchJob}
                  disabledReason={launchBlockedReason}
                  testId="harness-launch-button"
                />
              </div>
            }
          />
          <StepCard
            number={4}
            title="Observe / Input / Observe"
            body="Capture a frame, plan exact-target input, send one bounded action, and capture again."
            status={<StatusPill tone={observed ? "good" : "warn"}>{observed ? "Observed" : "Ready"}</StatusPill>}
            action={
              <div className="grid gap-2">
                <HarnessJobButton job={capturePlanJob} label="Plan capture" onRun={onRunWorkbenchJob} />
                <HarnessJobButton job={frameCaptureJob} label="Capture frame" onRun={onRunWorkbenchJob} />
                <HarnessJobButton job={inputPlanJob} label="Plan input" onRun={onRunWorkbenchJob} />
                <label className="flex items-start gap-2 rounded-md border border-workbench-border bg-white p-3 text-sm text-workbench-muted">
                  <input
                    className="mt-1"
                    type="checkbox"
                    checked={inputJobsArmed}
                    onChange={(event) => setInputJobsArmed(event.target.checked)}
                  />
                  <span>Confirm a managed BEA window is selected before sending input.</span>
                </label>
                <HarnessJobButton
                  job={inputSendJob}
                  label="Send input"
                  onRun={onRunWorkbenchJob}
                  disabledReason={inputBlockedReason}
                  testId="harness-send-input-button"
                />
              </div>
            }
          />
          <StepCard
            number={5}
            title="Stop and Review"
            body="Stop the managed process and record what was proven."
            status={<StatusPill tone={stopStatusTone}>{stopStatusLabel}</StatusPill>}
            action={
              <HarnessJobButton
                job={stopManagedProcessJob}
                label="Stop managed process"
                onRun={onRunWorkbenchJob}
                disabledReason={stopBlockedReason}
                testId="harness-stop-button"
                icon={Square}
              />
            }
          />
        </aside>

        <main className="grid gap-5">
          <Card>
            <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Current investigation</h3>
                <p className="mt-1 text-sm text-workbench-muted">Objective</p>
                <p className="mt-1 text-xl font-semibold text-workbench-text">Inspect textures used in Mission 3 sky sphere</p>
                <p className="mt-2 text-sm leading-6 text-workbench-muted">Confirm texture assets, material settings, and LOD behavior with a bounded observe/review loop.</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" disabled>
                  Create investigation
                </Button>
                <StatusPill tone="warn">Guided proof only</StatusPill>
              </div>
            </div>
            <p className="mb-4 rounded-lg border border-workbench-border bg-workbench-panel2 p-3 text-sm leading-6 text-workbench-muted">
              Guided proof flow is available; custom objective planning is a future maintainer feature.
            </p>
            <div className="grid gap-3 md:grid-cols-2">
              {([
                { title: "Observe", body: "Capture the managed game window and record the first frame status." },
                { title: "Decide", body: "Choose one bounded next action only if capture and target identity are ready." },
                { title: "Act", body: "Send only the selected safe input to the managed BEA window." },
                { title: "Evidence", body: "Record frame captures, selected action, target identity, and cleanup result." }
              ] satisfies Array<{ title: string; body: string }>).map((step, index) => (
                <div key={step.title} className="flex gap-3 rounded-lg border border-workbench-border bg-workbench-panel2 p-3">
                  <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#eaf1ff] text-sm font-semibold text-[#2457c5]">{index + 1}</span>
                  <div>
                    <p className="font-semibold text-workbench-text">{step.title}</p>
                    <p className="text-sm leading-6 text-workbench-muted">{step.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold text-workbench-text">Safety boundaries</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {["Read-only capture", "Exact-target input only", "Human confirmation required", "Copied profile only", "Stop process when done"].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-lg border border-workbench-border bg-workbench-panel2 p-3">
                  <CheckCircle2 className="h-5 w-5 text-[#16a34a]" aria-hidden="true" />
                  <p className="font-medium text-workbench-text">{item}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card data-testid="capture-window-plan">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Evidence</h3>
                <p className="mt-1 text-sm text-workbench-muted">Captured observations and bounded actions appear here.</p>
              </div>
              <StatusPill tone={observed ? "good" : "warn"}>{observed ? "Captured" : "No evidence yet"}</StatusPill>
            </div>
            {observed || inputPlanned ? (
              <div className="grid gap-3 md:grid-cols-3">
                {frameCaptureRun ? <MetricCard label="Frame capture" value={frameCaptureRun.status} detail={frameCaptureRun.result.summary} tone={frameCaptureRun.status === "completed" ? "good" : "warn"} /> : null}
                {frameSequenceRun ? <MetricCard label="Sequence" value={frameSequenceRun.status} detail={frameSequenceRun.result.summary} tone={frameSequenceRun.status === "completed" ? "good" : "warn"} /> : null}
                {inputRun ? <MetricCard label="Input" value={inputRun.status} detail={inputRun.result.summary} tone={inputRun.status === "completed" ? "good" : "warn"} /> : null}
              </div>
            ) : (
              <EmptyState icon={Camera} title="No evidence yet." body="Start the investigation to capture the first observation." />
            )}
            <DetailsDisclosure className="mt-4" title="Capture and input details" summary="Show managed target fields">
              <DetailGrid>
                <DetailTile label="Copied executable" value={fileNameFromPath(copiedExecutablePath)} detail={safeSummary(copiedExecutablePath)} />
                <DetailTile label="Capture plan" value={capturePlanRun?.status ?? "Not run"} />
                <DetailTile label="Patch result" value={patchWorkflowRun?.status ?? "Not applied"} detail={patchWorkflowError ?? undefined} />
              </DetailGrid>
            </DetailsDisclosure>
          </Card>
        </main>

        <aside className="grid gap-4 self-start">
          <Card data-testid="agentic-loop-readiness">
            <h3 className="text-lg font-semibold text-workbench-text">The agentic loop</h3>
            <p className="mt-1 text-sm text-workbench-muted">How Onslaught works at runtime.</p>
            <div className="mt-4 grid gap-3">
              {([
                { icon: Eye, title: "Observe", body: "Capture what is happening and gather data." },
                { icon: Target, title: "Decide", body: "Analyze observations and choose the next bounded action." },
                { icon: Gamepad2, title: "Act", body: "Perform the precise approved action." },
                { icon: CheckCircle2, title: "Review", body: "Check results, validate progress, and stop or continue." }
              ] satisfies Array<{ icon: LucideIcon; title: string; body: string }>).map(({ icon: Icon, title, body }) => (
                <div key={String(title)} className="flex gap-3 rounded-lg border border-workbench-border bg-white p-3">
                  <Icon className="h-6 w-6 shrink-0 text-[#2457c5]" aria-hidden="true" />
                  <div>
                    <p className="font-semibold text-workbench-text">{title}</p>
                    <p className="text-sm leading-6 text-workbench-muted">{body}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold text-workbench-text">Session status</h3>
            <div className="mt-4 grid gap-2">
              <StatusRow label="Game" value={launchRunning ? "Running" : launchCompleted ? "Launch recorded" : "Not launched"} tone={launchStatusTone} />
              <StatusRow label="Loop" value={observed ? "Observed" : "Inactive"} tone={observed ? "good" : "neutral"} />
              <StatusRow label="Evidence" value={observed ? "Items available" : "0 items"} tone={observed ? "good" : "neutral"} />
              <StatusRow label="Duration" value="00:00:00" tone="neutral" />
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold text-workbench-text">Game folder</h3>
            <label className="mt-3 grid gap-2 text-sm">
              <span className="font-medium text-workbench-text">Local game folder</span>
              <input
                className="min-h-10 rounded-md border border-workbench-border bg-white px-3 text-sm text-workbench-text outline-none focus:border-[#9db7f5] focus:ring-2 focus:ring-[#dbe7ff]"
                placeholder="Choose your game folder"
                value={gameFolderPath}
                onChange={(event) => onGameFolderPathChange(event.target.value)}
              />
            </label>
            <div className="mt-3 flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => void onBrowseGameFolder()} disabled={gameFolderBusy}>
                <HardDrive className="h-4 w-4" aria-hidden="true" />
                Browse
              </Button>
              <Button variant="secondary" onClick={() => void onUseGameFolder()} disabled={gameFolderBusy}>
                Use folder
              </Button>
              <Button variant="secondary" onClick={() => void onResetGameFolder()} disabled={gameFolderBusy}>
                <RotateCcw className="h-4 w-4" aria-hidden="true" />
                Reset
              </Button>
            </div>
            {gameFolderError || safeProfileError ? (
              <p className="mt-3 rounded-md border border-[#fecdca] bg-[#fef3f2] p-3 text-sm text-[#b42318]">{gameFolderError ?? safeProfileError}</p>
            ) : null}
            <DetailsDisclosure className="mt-4" title="Profile details" summary="Show local paths">
              <DetailGrid>
                <DetailTile label="Profile source" value={gameHarnessProfile?.profileSource ?? "Not checked"} />
                <DetailTile label="Working folder" value={fileNameFromPath(gameHarnessProfile?.workingDirectory)} detail={safeSummary(gameHarnessProfile?.workingDirectory)} />
                <DetailTile label="Recommended args" value={gameHarnessProfile?.recommendedArgs.join(" ") || "None"} />
              </DetailGrid>
            </DetailsDisclosure>
          </Card>
        </aside>
      </div>
    </PageSection>
  );
}

function HarnessJobButton({
  job,
  label,
  onRun,
  disabledReason,
  testId = "harness-job-button",
  icon: Icon = Play
}: {
  job: WorkbenchJobDefinition | null;
  label: string;
  onRun: (job: WorkbenchJobDefinition) => void | Promise<void>;
  disabledReason?: string;
  testId?: string;
  icon?: LucideIcon;
}) {
  const unavailableReason = !job ? "Tool is unavailable." : job.status !== "available" ? "Tool is not ready." : undefined;
  const reason = disabledReason ?? unavailableReason;
  return (
    <div className="grid gap-1">
      <Button
        variant="secondary"
        data-testid={testId}
        data-job-id={job?.id ?? "none"}
        disabled={Boolean(reason)}
        onClick={() => job && !reason && void onRun(job)}
      >
        <Icon className="h-4 w-4" aria-hidden="true" />
        {label}
      </Button>
      {reason ? <p className="text-xs leading-5 text-workbench-muted">{reason}</p> : null}
    </div>
  );
}

function StatusRow({ label, value, tone }: { label: string; value: string; tone: Tone }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-workbench-border bg-workbench-panel2 p-3 text-sm">
      <span className="text-workbench-muted">{label}</span>
      <StatusPill tone={tone}>{value}</StatusPill>
    </div>
  );
}

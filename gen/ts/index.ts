// Generated TypeScript bindings for @platform/contracts v0.1.0
// Do not edit by hand â€” regenerate from schemas/ using openapi-typescript and json-schema-to-typescript.

export type { paths as AiGatewayRequestPaths, components as AiGatewayRequestComponents } from "./ai-gateway-request";
export type { paths as AiGatewayPreflightPaths, components as AiGatewayPreflightComponents } from "./ai-gateway-preflight";
export type { paths as AiGatewayJobPaths, components as AiGatewayJobComponents } from "./ai-gateway-job";
export type { paths as AiGatewayResearchPaths, components as AiGatewayResearchComponents } from "./ai-gateway-research";
export type { paths as AppManifestPaths, components as AppManifestComponents } from "./app-manifest";
export type { paths as AppHealthPaths, components as AppHealthComponents } from "./app-health";
export type { UsageEvent } from "./usage-event";
export type { DimensionEvent } from "./dimension-event";
export type { TelemetryLogRecord } from "./telemetry";
export type { BuildCommand } from "./build-command";
export type { BuildResult } from "./build-result";
export type {
  StateEvent,
  ComponentHealthEvent, ComponentHealthPayload,
  LoadEvent, LoadPayload,
  CostTickEvent, CostTickPayload,
  CiRunEvent, CiRunPayload, CiRunStep, CiRunStepStatus, CiRunStepConclusion,
  AppStatusEvent, AppStatusPayload,
  ActivityCountEvent, ActivityCountPayload,
  JobProgressEvent, JobProgressPayload,
  AgentRunEvent, AgentRunPayload,
  DesignMissionEvent, DesignMissionPayload,
  DesignSystemEvent, DesignSystemPayload,
  AppMissionEvent, AppMissionPayload,
} from "./state-event";
export type { HexagonDescriptor } from "./hexagon-descriptor";
export type { RegistryEntry } from "./registry-entry";
export type { ConnectorVocabulary, Verb } from "./connector-vocabulary";
export type { ConnectorInvokeRequest } from "./connector-invoke-request";
export type { ConnectorInvokeResponse } from "./connector-invoke-response";
export type { Demand } from "./demand";
export type { DemandFulfillment } from "./demand-fulfillment";
export type { DemandQueueEntry } from "./demand-queue-entry";
export type { AiModelManifest, CapabilityDeclaration } from "./model-manifest";
export type { paths as StageCompanionTurnPaths, components as StageCompanionTurnComponents } from "./stage-companion-turn";
export type { AppMission, MissionStage, MissionGateStage, WaveReviewNext } from "./app-mission";
export type { AppTaskPlan, Wave, WorkUnit, VerifyStep } from "./app-task-plan";
export type { PlannerProject } from "./planner-project";
export type { PlannerModel } from "./planner-model";
export type { PlannerPlanRequest } from "./planner-plan-request";
export type { PlannerPlanIssue } from "./planner-plan-issue";
export type { PlannerPlanSummary } from "./planner-plan-summary";
export type { PlannerPlanRun } from "./planner-plan-run";
export type { PlannerConfirmRequest } from "./planner-confirm-request";
export type { PlannerError } from "./planner-error";
export type { DeliveryIssueRef } from "./delivery-issue-ref";
export type { DeliveryIssue, DeliveryIssueState, DeliveryIssueScope, DeliveryIssueDependency, DeliveryIssueLink } from "./delivery-issue";
export type { DeliveryIssuePage, DeliveryIssueQuery, DeliveryUnavailableProject } from "./delivery-issue-page";
export type { DeliveryWorkflow, DeliveryWorkflowState, DeliveryStartable } from "./delivery-workflow";
export type { DeliverySyncRequest, DeliveryCorrelation, DeliveryLinkPayload, DeliveryCommentPayload, DeliveryTransitionPayload, DeliveryResolvePayload, DeliveryAcceptanceRef } from "./delivery-sync-request";
export type { DeliverySyncOperation, DeliveryReadBack } from "./delivery-sync-operation";
export type { DeliveryOperationCoverage } from "./delivery-operation-coverage";
export type { DeliveryError } from "./delivery-error";
export type { DeliveryEvidence, DeliveryCriterionCoverage, DeliveryScopeBinding, DeliveryEvidenceSource, DeliveryEnvironment, DeliveryLegacyReceiptRef } from "./delivery-evidence";
export type { DeliveryDecision, DeliveryPolicyRef } from "./delivery-decision";
export type { DeliveryProducerResult, DeliveryProducerCorrelation, DeliveryProducerCheck } from "./delivery-producer-result";
// delivery-deployment-receipt.ts also inlines copies of AppDeploymentIdentity,
// DeliveryProducerCheck and DeliveryProducerCorrelation (cross-file $refs, same
// duplication as noted below). The canonical exports are the owning modules.
export type { DeliveryDeploymentReceipt, DeliveryImageDigests, DeliveryDeploymentEnvironment, DeliveryRollbackIdentity } from "./delivery-deployment-receipt";
export type { DeliveryDefectTaskRequest } from "./delivery-defect-task-request";
export type { DeliveryDefectTask } from "./delivery-defect-task";
export type { AppDeploymentIdentity } from "./deployment-identity";
export type { RunnerDispatchRequest } from "./runner-dispatch-request";
export type { RunnerRunRecord, RunnerRunWorkspace, RunnerRunFallback, RunnerUsageSegment } from "./runner-run-record";
// Only the reservation itself is re-exported here. Its `run` property `$ref`s
// runner.run-record.json, which json-schema-to-typescript resolves by INLINING a
// second copy of RunnerRunRecord/RunnerRunWorkspace into this module (the same
// duplication delivery-producer-result.ts has for DeliveryEnvironment, whose
// canonical export is likewise the module that owns the schema). Re-exporting them
// from both modules would collide; RunnerRunRecord and RunnerRunWorkspace above are
// the canonical ones. Both copies are generated from the same file in the same run,
// so they cannot drift.
export type { RunnerDispatchReservation } from "./runner-dispatch-reservation";

// D143 brain v1 wire shapes (spec-agent-memory-system.md v1.0). brain-run-record.ts, brain-job.ts and
// brain-repo-summary.ts each INLINE a copy of the types they $ref (BrainCliResult, BrainJob), the same
// json-schema-to-typescript duplication as above, so BrainCliResult is exported from its own module and
// BrainJob from brain-job.ts only.
export type { BrainCliResult } from "./brain-cli-result";
export type { BrainRunRecord, BrainRunLine, BrainJobLine } from "./brain-run-record";
export type { BrainRunBundle } from "./brain-run-bundle";
export type { BrainChange } from "./brain-change";
export type { BrainNote } from "./brain-note";
export type { BrainCandidate } from "./brain-candidate";
export type { BrainFunctions, BrainFunction } from "./brain-functions";
export type { BrainJob } from "./brain-job";
export type { BrainJobRequest } from "./brain-job-request";
export type { BrainRepoSummary, BrainLastRun } from "./brain-repo-summary";
export type { BrainUsage, BrainUsageDay } from "./brain-usage";
// D143 addendum 2026-10-27: settings, statistics and the job page. brain-stats.ts and brain-job-page.ts inline copies of
// BrainUsage / BrainJob / BrainCliResult (same $ref duplication as above), so only the canonical copies are re-exported.
export type { BrainSettings, BrainSettingsFunction, BrainShippedDefault } from "./brain-settings";
export type { BrainSettingsUpdate, BrainSettingsFunctionUpdate } from "./brain-settings-update";
export type { BrainSettingsAuditEntry } from "./brain-settings-audit-entry";
export type { BrainStats, BrainStatsTotals, BrainStatsJobs, BrainStatsRepo } from "./brain-stats";
export type { BrainJobPage, BrainJobFilters } from "./brain-job-page";

// D115 parked work. parked-run-result.ts and parked-resume-request.ts each INLINE a copy of the
// types they $ref (json-schema-to-typescript), so only each schema's own top-level type is
// exported from them; the condition and outcome types come from their defining modules.
export type {
  ParkedWaitCondition, CiRunCondition, PullRequestCondition, RepositoryCreatedCondition,
  OwnerDecisionCondition, DemandsCondition,
} from "./parked-wait-condition";
export type { ParkedRunResult } from "./parked-run-result";
export type {
  ParkedConditionEvent, CiRunOutcome, PullRequestOutcome, RepositoryCreatedOutcome,
  OwnerDecisionOutcome, DemandsOutcome,
} from "./parked-condition-event";
export type { ParkedResumeRequest } from "./parked-resume-request";

// D115 command-execution port (launcher).
export type { CommandRequest } from "./command-request";
export type { CommandResult } from "./command-result";
export type { CommandError } from "./command-error";

// app.descriptor (app.yaml) — distinct from app.manifest.
export type { AppDescriptor } from "./app-descriptor";
export type { PlannerBriefProjectRequest } from "./planner-brief-project-request";
export type { PlannerBriefProjectResponse } from "./planner-brief-project-response";
export type { PlannerBriefProjectError } from "./planner-brief-project-error";
export type { PlannerSetupProgressRequest } from "./planner-setup-progress-request";
export type { PlannerSetupProgressResponse } from "./planner-setup-progress-response";
export type { PlannerSetupGate } from "./planner-setup-gate";
export type { PlannerSetupError } from "./planner-setup-error";
export type { FactoryHandoverSetup } from "./factory-handover-setup";

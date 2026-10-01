// Generated TypeScript bindings for @platform/contracts v0.1.0
// Do not edit by hand — regenerate from schemas/ using openapi-typescript and json-schema-to-typescript.

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
export type { DeliveryWorkflow, DeliveryWorkflowState } from "./delivery-workflow";
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
export type { AppDeploymentIdentity } from "./deployment-identity";
export type { RunnerDispatchRequest } from "./runner-dispatch-request";
export type { RunnerRunRecord, RunnerRunWorkspace } from "./runner-run-record";
// Only the reservation itself is re-exported here. Its `run` property `$ref`s
// runner.run-record.json, which json-schema-to-typescript resolves by INLINING a
// second copy of RunnerRunRecord/RunnerRunWorkspace into this module (the same
// duplication delivery-producer-result.ts has for DeliveryEnvironment, whose
// canonical export is likewise the module that owns the schema). Re-exporting them
// from both modules would collide; RunnerRunRecord and RunnerRunWorkspace above are
// the canonical ones. Both copies are generated from the same file in the same run,
// so they cannot drift.
export type { RunnerDispatchReservation } from "./runner-dispatch-reservation";

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

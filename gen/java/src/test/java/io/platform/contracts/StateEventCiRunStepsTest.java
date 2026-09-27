package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.events.CiRunEvent;
import io.platform.contracts.events.CiRunStep;
import io.platform.contracts.events.CiRunStepConclusion;
import io.platform.contracts.events.CiRunStepStatus;
import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * v0.30.0 adds optional jobId + steps[] to CiRunPayload, so a CI job's per-step progress
 * can reach the dashboard as a stage view (demand plantpal-20260927-contracts-ci-run-steps).
 *
 * <p>Purely additive: a pre-v0.30.0 ci.run without either field must still deserialize.
 * jobId is GitHub's workflow_job.id — above Integer.MAX_VALUE in practice, same as runId
 * (see RunIdOverflowRegressionTest), so it must bind to Long.
 */
class StateEventCiRunStepsTest {

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    private static final String PAYLOAD_HEAD = "\"runId\":9876543210,\"repo\":\"owner/contracts\",\"ref\":\"main\","
            + "\"workflow\":\"ci\",\"jobName\":\"sonar-gate\",\"runnerLabels\":[\"self-hosted\"],";

    @Test
    void eventWithoutJobIdOrStepsStillDeserializes() throws Exception {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:00:00Z\","
                + "\"payload\":{" + PAYLOAD_HEAD + "\"phase\":\"queued\"}}";

        CiRunEvent event = mapper.readValue(json, CiRunEvent.class);

        assertNull(event.getPayload().getJobId());
        List<CiRunStep> steps = event.getPayload().getSteps();
        assertTrue(steps == null || steps.isEmpty());
    }

    @Test
    void stepsDeserializeInOrderWithEnums() throws Exception {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:05:00Z\","
                + "\"payload\":{" + PAYLOAD_HEAD + "\"phase\":\"in_progress\",\"jobId\":31234567890,"
                + "\"steps\":["
                + "{\"number\":1,\"name\":\"Set up job\",\"status\":\"completed\",\"conclusion\":\"success\","
                + "\"startedAt\":\"2026-09-27T08:59:00Z\",\"completedAt\":\"2026-09-27T08:59:05Z\"},"
                + "{\"number\":2,\"name\":\"Sonar scan\",\"status\":\"in_progress\"},"
                + "{\"number\":3,\"name\":\"Quality gate\",\"status\":\"queued\"}"
                + "]},\"origin\":\"host\"}";

        CiRunEvent event = mapper.readValue(json, CiRunEvent.class);

        assertEquals(31234567890L, event.getPayload().getJobId());
        List<CiRunStep> steps = event.getPayload().getSteps();
        assertEquals(3, steps.size());
        assertEquals(CiRunStepStatus.COMPLETED, steps.get(0).getStatus());
        assertEquals(CiRunStepConclusion.SUCCESS, steps.get(0).getConclusion());
        assertEquals(CiRunStepStatus.IN_PROGRESS, steps.get(1).getStatus());
        assertNull(steps.get(1).getConclusion());
        assertEquals("Quality gate", steps.get(2).getName());
        assertEquals(3, steps.get(2).getNumber());
    }

    @Test
    void unknownStepStatusIsRejected() {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:05:00Z\","
                + "\"payload\":{" + PAYLOAD_HEAD + "\"phase\":\"in_progress\","
                + "\"steps\":[{\"number\":1,\"name\":\"Set up job\",\"status\":\"running\"}]}}";

        assertThrows(JsonMappingException.class, () -> mapper.readValue(json, CiRunEvent.class));
    }

    @Test
    void timedOutIsNotAStepConclusion() {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:05:00Z\","
                + "\"payload\":{" + PAYLOAD_HEAD + "\"phase\":\"completed\",\"conclusion\":\"timed_out\","
                + "\"steps\":[{\"number\":1,\"name\":\"Sonar scan\",\"status\":\"completed\",\"conclusion\":\"timed_out\"}]}}";

        assertThrows(JsonMappingException.class, () -> mapper.readValue(json, CiRunEvent.class));
    }

    @Test
    void roundTripsBackToTheSameShape() throws Exception {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:10:00Z\","
                + "\"payload\":{" + PAYLOAD_HEAD + "\"phase\":\"completed\",\"conclusion\":\"failure\","
                + "\"jobId\":31234567890,"
                + "\"steps\":[{\"number\":1,\"name\":\"Quality gate\",\"status\":\"completed\",\"conclusion\":\"failure\"}]}}";

        CiRunEvent event = mapper.readValue(json, CiRunEvent.class);
        CiRunEvent reparsed = mapper.readValue(mapper.writeValueAsString(event), CiRunEvent.class);

        assertEquals(event, reparsed);
    }
}

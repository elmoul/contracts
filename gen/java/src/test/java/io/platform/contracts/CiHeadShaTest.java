package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.cirunner.BuildResult;
import io.platform.contracts.events.CiRunEvent;
import org.junit.jupiter.api.Test;

/**
 * v0.34.0 adds optional headSha (full 40-hex commit SHA) to ci.run's CiRunPayload and to
 * BuildResult, so a CI job can be tied to an exact revision
 * (demand ci-runner-20260927-contracts-ci-headsha-lookup).
 *
 * <p>Purely additive: a pre-v0.34.0 ci.run or BuildResult without headSha must still
 * deserialize, and headSha is absent (null) rather than defaulted. The schema pattern is
 * lowercase-only (^[0-9a-f]{40}$), matching every other revision field in the platform, so
 * this test also pins that a null binding means "not observed", never a guess at ref.
 */
class CiHeadShaTest {

    private static final String SHA = "0123456789abcdef0123456789abcdef01234567";

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    private static final String CI_PAYLOAD_HEAD = "\"runId\":9876543210,\"repo\":\"owner/contracts\","
            + "\"ref\":\"main\",\"workflow\":\"ci\",\"jobName\":\"sonar-gate\","
            + "\"runnerLabels\":[\"self-hosted\"],";

    @Test
    void ciRunWithoutHeadShaStillDeserializes() throws Exception {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:00:00Z\","
                + "\"payload\":{" + CI_PAYLOAD_HEAD + "\"phase\":\"queued\"}}";

        CiRunEvent event = mapper.readValue(json, CiRunEvent.class);

        assertNull(event.getPayload().getHeadSha());
    }

    @Test
    void ciRunBindsHeadShaAndRoundTrips() throws Exception {
        String json = "{\"type\":\"ci.run\",\"timestamp\":\"2026-09-27T09:05:00Z\","
                + "\"payload\":{" + CI_PAYLOAD_HEAD + "\"phase\":\"completed\",\"conclusion\":\"success\","
                + "\"jobId\":31234567890,\"headSha\":\"" + SHA + "\"},\"origin\":\"host\"}";

        CiRunEvent event = mapper.readValue(json, CiRunEvent.class);
        assertEquals(SHA, event.getPayload().getHeadSha());

        CiRunEvent reparsed = mapper.readValue(mapper.writeValueAsString(event), CiRunEvent.class);
        assertEquals(event, reparsed);
    }

    @Test
    void buildResultWithoutHeadShaStillDeserializes() throws Exception {
        String json = "{\"correlationId\":\"c-1\",\"repo\":\"owner/contracts\",\"ref\":\"main\","
                + "\"runId\":9876543210,\"status\":\"success\",\"completedAt\":\"2026-09-27T09:00:00Z\"}";

        BuildResult result = mapper.readValue(json, BuildResult.class);

        assertNull(result.getHeadSha());
        assertEquals("main", result.getRef());
    }

    @Test
    void buildResultBindsHeadShaAndRoundTrips() throws Exception {
        String json = "{\"correlationId\":\"c-1\",\"repo\":\"owner/contracts\",\"ref\":\"main\","
                + "\"headSha\":\"" + SHA + "\",\"runId\":9876543210,\"status\":\"failure\","
                + "\"completedAt\":\"2026-09-27T09:00:00Z\"}";

        BuildResult result = mapper.readValue(json, BuildResult.class);
        assertEquals(SHA, result.getHeadSha());
        assertEquals(BuildResult.Status.FAILURE, result.getStatus());

        BuildResult reparsed = mapper.readValue(mapper.writeValueAsString(result), BuildResult.class);
        assertEquals(result, reparsed);
    }

    @Test
    void buildResultWithNullHeadShaIsNotFilledFromRef() throws Exception {
        // "not observed" stays null; ref is a moving name and must never be promoted to a revision.
        String json = "{\"correlationId\":\"c-1\",\"repo\":\"owner/contracts\",\"ref\":\"" + SHA + "\","
                + "\"runId\":9876543210,\"status\":\"success\",\"completedAt\":\"2026-09-27T09:00:00Z\"}";

        BuildResult result = mapper.readValue(json, BuildResult.class);

        assertNull(result.getHeadSha());
        assertTrue(result.getRef().equals(SHA));
    }
}

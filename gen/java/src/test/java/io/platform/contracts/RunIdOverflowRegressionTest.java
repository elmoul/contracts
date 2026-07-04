package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.cirunner.BuildResult;
import io.platform.contracts.events.CiRunPayload;
import org.junit.jupiter.api.Test;

/**
 * A real workflow_dispatch run's 11-digit runId (28714195292) overflows a 32-bit int
 * and was rejected by control-plane's /ci/results endpoint (HttpMessageNotReadableException:
 * "Numeric value (28714195292) out of range of int"). Both runId fields must stay Long.
 */
class RunIdOverflowRegressionTest {

    private static final long ELEVEN_DIGIT_RUN_ID = 28714195292L;

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void buildResultDeserializesElevenDigitRunId() throws Exception {
        String json = "{"
                + "\"correlationId\":\"c-1\","
                + "\"repo\":\"elmoul/plant-pal\","
                + "\"ref\":\"main\","
                + "\"runId\":" + ELEVEN_DIGIT_RUN_ID + ","
                + "\"status\":\"success\","
                + "\"completedAt\":\"2026-07-04T12:00:00Z\""
                + "}";

        BuildResult result = mapper.readValue(json, BuildResult.class);

        assertEquals(ELEVEN_DIGIT_RUN_ID, result.getRunId());
    }

    @Test
    void ciRunPayloadDeserializesElevenDigitRunId() throws Exception {
        String json = "{"
                + "\"runId\":" + ELEVEN_DIGIT_RUN_ID + ","
                + "\"repo\":\"elmoul/plant-pal\","
                + "\"ref\":\"main\","
                + "\"workflow\":\"build\","
                + "\"jobName\":\"build\","
                + "\"phase\":\"completed\","
                + "\"runnerLabels\":[\"self-hosted\"]"
                + "}";

        CiRunPayload payload = mapper.readValue(json, CiRunPayload.class);

        assertEquals(ELEVEN_DIGIT_RUN_ID, payload.getRunId());
    }
}

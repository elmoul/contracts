package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.conventions.ConventionsRule;
import io.platform.contracts.conventions.ConventionsRun;
import io.platform.contracts.spec.SpecDriftItem;
import io.platform.contracts.spec.SpecStatus;
import org.junit.jupiter.api.Test;

/**
 * D144: conventions compliance and living-spec shapes. control-plane (Java) serves
 * /conventions/*, so the rule and run must deserialize from the validator's JSON.
 */
class ConventionsContractsRoundTripTest {

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void ruleDeserializes() throws Exception {
        String json = "{"
                + "\"id\":\"loopback-only-ports\",\"category\":\"runtime-posture\","
                + "\"rule\":\"Every published container port binds 127.0.0.1.\","
                + "\"applies_to\":{\"has_file\":[\"docker-compose.yml\"]},"
                + "\"source\":[\"D040\"],\"amended_by\":[\"D120\"],"
                + "\"enforced_by\":\"check:loopback-ports\",\"severity\":\"fail\","
                + "\"exceptions\":[{\"path\":\"launcher/tailnet.*\",\"reason\":\"D120\"}],"
                + "\"status\":\"active\",\"as_of\":\"2026-10-27\""
                + "}";

        ConventionsRule rule = mapper.readValue(json, ConventionsRule.class);

        assertEquals("loopback-only-ports", rule.getId());
        assertEquals("docker-compose.yml", rule.getAppliesTo().getHasFile().get(0));
        assertEquals(ConventionsRule.Severity.FAIL, rule.getSeverity());
        assertEquals("launcher/tailnet.*", rule.getExceptions().get(0).getPath());
    }

    @Test
    void runWithSkippedRepoAndRulelessFindingDeserializes() throws Exception {
        String json = "{"
                + "\"id\":\"run-1\",\"startedAt\":\"2026-10-28T02:00:00Z\",\"finishedAt\":null,"
                + "\"validatorSource\":\"a1b2c3d\",\"catalogHash\":\"h\",\"trigger\":\"nightly\","
                + "\"repos\":[{\"repo\":\"contracts\",\"sha\":null,\"result\":\"skipped\",\"checks\":["
                + "{\"checkId\":\"readme\",\"ruleId\":null,\"status\":\"skipped\",\"message\":\"m\",\"file\":null,\"line\":null}"
                + "]}]}";

        ConventionsRun run = mapper.readValue(json, ConventionsRun.class);

        assertNull(run.getFinishedAt());
        assertNull(run.getRepos().get(0).getSha());
        assertNull(run.getRepos().get(0).getChecks().get(0).getRuleId());
    }

    @Test
    void specStatusAndDriftItemDeserialize() throws Exception {
        String status = "{"
                + "\"hexagon\":\"ai-gateway\",\"kind\":\"runtime\",\"specPath\":\"spec-ai-gateway.md\","
                + "\"specVersion\":null,\"contractAsOf\":null,\"stateAsOf\":null,\"verifiedAgainst\":null,"
                + "\"commitsSince\":null,\"driftCount\":0,\"openQuestions\":0,\"reviewWindowDays\":90,"
                + "\"due\":true,\"lastJob\":null,\"v2\":false}";
        String drift = "{\"id\":\"d-1\",\"kind\":\"planned-now-built\",\"summary\":\"s\","
                + "\"file\":null,\"line\":null,\"contractSection\":\"8. Planned, not built\"}";

        SpecStatus s = mapper.readValue(status, SpecStatus.class);
        SpecDriftItem d = mapper.readValue(drift, SpecDriftItem.class);

        assertEquals(Boolean.FALSE, s.getV2());
        assertNull(s.getLastJob());
        assertEquals(SpecDriftItem.Kind.PLANNED_NOW_BUILT, d.getKind());
    }
}

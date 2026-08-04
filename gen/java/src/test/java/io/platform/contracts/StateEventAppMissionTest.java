package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.exc.ValueInstantiationException;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.events.AppMissionEvent;
import io.platform.contracts.events.AppMissionPayload;
import io.platform.contracts.events.Origin;
import org.junit.jupiter.api.Test;

/**
 * v0.20.0 adds app.mission as the eleventh state.event oneOf member, so state-feed can
 * accept app-studio's mission transitions type-safely (demand
 * state-feed-20260804-state-event-app-mission-member).
 *
 * <p>The stage/gate vocabularies are app.mission.json's own (missionStage /
 * missionGateStage) — these tests pin that the Java binding really generates them as
 * enums rather than free strings, which is the whole point of the union member. That
 * the two enum copies stay equal to app.mission.json is enforced separately, on the
 * schema files themselves, by tests/check_state_event_sync.py.
 */
class StateEventAppMissionTest {

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void gatelessTransitionDeserializes() throws Exception {
        String json = "{"
                + "\"type\":\"app.mission\","
                + "\"timestamp\":\"2026-08-04T09:00:00Z\","
                + "\"payload\":{"
                + "\"missionId\":\"d34de281-c5c5-4e44-b3c5-6085c225adea\","
                + "\"appName\":\"tutor\",\"stage\":\"executing\",\"currentWave\":2}"
                + "}";

        AppMissionEvent event = mapper.readValue(json, AppMissionEvent.class);

        assertEquals(AppMissionEvent.TypeEnum.APP_MISSION, event.getType());
        assertEquals(AppMissionPayload.StageEnum.EXECUTING, event.getPayload().getStage());
        assertEquals(2, event.getPayload().getCurrentWave());
        assertNull(event.getPayload().getGate());
        assertNull(event.getPayload().getOutcome());
        assertNull(event.getOrigin());
    }

    @Test
    void waveReviewOutcomeCarriesGateAndWave() throws Exception {
        String json = "{"
                + "\"type\":\"app.mission\","
                + "\"timestamp\":\"2026-08-04T09:05:00Z\","
                + "\"payload\":{"
                + "\"missionId\":\"d34de281-c5c5-4e44-b3c5-6085c225adea\","
                + "\"appName\":\"tutor\",\"stage\":\"wave-review\",\"currentWave\":2,"
                + "\"gate\":\"wave-review\",\"outcome\":\"rejected\",\"gateWave\":2},"
                + "\"origin\":\"host\""
                + "}";

        AppMissionEvent event = mapper.readValue(json, AppMissionEvent.class);

        assertEquals(AppMissionPayload.GateEnum.WAVE_REVIEW, event.getPayload().getGate());
        assertEquals(AppMissionPayload.OutcomeEnum.REJECTED, event.getPayload().getOutcome());
        assertEquals(2, event.getPayload().getGateWave());
        assertEquals(Origin.HOST, event.getOrigin());
    }

    @Test
    void terminalAbortedStageIsOnTheSpine() throws Exception {
        String json = "{"
                + "\"type\":\"app.mission\","
                + "\"timestamp\":\"2026-08-04T09:15:00Z\","
                + "\"payload\":{"
                + "\"missionId\":\"d34de281-c5c5-4e44-b3c5-6085c225adea\","
                + "\"appName\":\"tutor\",\"stage\":\"aborted\",\"currentWave\":1}"
                + "}";

        AppMissionEvent event = mapper.readValue(json, AppMissionEvent.class);

        assertEquals(AppMissionPayload.StageEnum.ABORTED, event.getPayload().getStage());
    }

    @Test
    void designStudioStageNameIsRejected() {
        String json = "{"
                + "\"type\":\"app.mission\","
                + "\"timestamp\":\"2026-08-04T09:00:00Z\","
                + "\"payload\":{"
                + "\"missionId\":\"d34de281-c5c5-4e44-b3c5-6085c225adea\","
                + "\"appName\":\"tutor\",\"stage\":\"feel-gate\",\"currentWave\":0}"
                + "}";

        assertThrows(ValueInstantiationException.class, () -> mapper.readValue(json, AppMissionEvent.class));
    }

    @Test
    void sendBackIsNotAGateOutcome() {
        String json = "{"
                + "\"type\":\"app.mission\","
                + "\"timestamp\":\"2026-08-04T09:00:00Z\","
                + "\"payload\":{"
                + "\"missionId\":\"d34de281-c5c5-4e44-b3c5-6085c225adea\","
                + "\"appName\":\"tutor\",\"stage\":\"plan-gate\",\"currentWave\":0,"
                + "\"gate\":\"plan-gate\",\"outcome\":\"send-back\"}"
                + "}";

        assertThrows(ValueInstantiationException.class, () -> mapper.readValue(json, AppMissionEvent.class));
    }

    @Test
    void roundTripsBackToTheSameJsonShape() throws Exception {
        String json = "{"
                + "\"type\":\"app.mission\","
                + "\"timestamp\":\"2026-08-04T09:10:00Z\","
                + "\"payload\":{"
                + "\"missionId\":\"d34de281-c5c5-4e44-b3c5-6085c225adea\","
                + "\"appName\":\"tutor\",\"stage\":\"concept-gate\",\"currentWave\":0,"
                + "\"gate\":\"concept-gate\",\"outcome\":\"approved\"}"
                + "}";

        AppMissionEvent event = mapper.readValue(json, AppMissionEvent.class);
        AppMissionEvent reparsed = mapper.readValue(mapper.writeValueAsString(event), AppMissionEvent.class);

        assertEquals(event, reparsed);
    }
}

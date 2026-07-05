package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.events.ActivityCountEvent;
import io.platform.contracts.events.Origin;
import org.junit.jupiter.api.Test;

/**
 * v0.7.0 adds the activity.count event, replacing repurposed load pulses for hub
 * activity counters. count is a delta since the last emission for a
 * (componentId, activity) pair, not a cumulative total.
 */
class StateEventActivityCountTest {

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void activityCountEventDeserializesWithOrigin() throws Exception {
        String json = "{"
                + "\"type\":\"activity.count\","
                + "\"timestamp\":\"2026-07-05T12:00:00Z\","
                + "\"payload\":{\"componentId\":\"sentinel-hub\",\"activity\":\"scan.message\",\"count\":7},"
                + "\"origin\":\"hub\""
                + "}";

        ActivityCountEvent event = mapper.readValue(json, ActivityCountEvent.class);

        assertEquals(Origin.HUB, event.getOrigin());
        assertEquals("sentinel-hub", event.getPayload().getComponentId());
        assertEquals("scan.message", event.getPayload().getActivity());
        assertEquals(7, event.getPayload().getCount());
    }

    @Test
    void activityCountEventDeserializesWithoutOrigin() throws Exception {
        String json = "{"
                + "\"type\":\"activity.count\","
                + "\"timestamp\":\"2026-07-05T12:00:00Z\","
                + "\"payload\":{\"componentId\":\"orchestrator\",\"activity\":\"tool.call\",\"count\":0}"
                + "}";

        ActivityCountEvent event = mapper.readValue(json, ActivityCountEvent.class);

        assertNull(event.getOrigin());
        assertEquals(0, event.getPayload().getCount());
    }

    @Test
    void activityCountEventRejectsUnknownProperty() {
        String json = "{"
                + "\"type\":\"activity.count\","
                + "\"timestamp\":\"2026-07-05T12:00:00Z\","
                + "\"payload\":{\"componentId\":\"orchestrator\",\"activity\":\"tool.call\",\"count\":1,\"extra\":\"nope\"}"
                + "}";

        assertThrows(JsonMappingException.class, () -> mapper.readValue(json, ActivityCountEvent.class));
    }
}

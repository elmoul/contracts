package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.events.ComponentHealthEvent;
import io.platform.contracts.events.Origin;
import org.junit.jupiter.api.Test;

/**
 * v0.6.0 adds an optional 'origin' field to every state.event envelope (D011: host|hub).
 * Absent means host — existing producers that predate this field must keep deserializing.
 */
class StateEventOriginTest {

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    @Test
    void originTaggedEventDeserializes() throws Exception {
        String json = "{"
                + "\"type\":\"component.health\","
                + "\"timestamp\":\"2026-07-04T12:00:00Z\","
                + "\"payload\":{\"componentId\":\"connector-gmail\",\"status\":\"UP\"},"
                + "\"origin\":\"hub\""
                + "}";

        ComponentHealthEvent event = mapper.readValue(json, ComponentHealthEvent.class);

        assertEquals(Origin.HUB, event.getOrigin());
    }

    @Test
    void originLessEventStillDeserializes() throws Exception {
        String json = "{"
                + "\"type\":\"component.health\","
                + "\"timestamp\":\"2026-07-04T12:00:00Z\","
                + "\"payload\":{\"componentId\":\"treasury\",\"status\":\"UP\"}"
                + "}";

        ComponentHealthEvent event = mapper.readValue(json, ComponentHealthEvent.class);

        assertNull(event.getOrigin());
    }
}

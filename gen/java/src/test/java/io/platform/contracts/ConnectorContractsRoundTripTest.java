package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.platform.contracts.connector.ConnectorInvokeRequest;
import io.platform.contracts.connector.ConnectorInvokeResponse;
import io.platform.contracts.connector.ConnectorVocabulary;
import io.platform.contracts.connector.Verb;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Round-trip (serialize/deserialize) coverage for the new v0.6.0 connector schemas
 * (spec-connectors.md §2, §5-§6).
 */
class ConnectorContractsRoundTripTest {

    private final ObjectMapper mapper = new ObjectMapper();

    @Test
    void connectorVocabularyRoundTrips() throws Exception {
        ConnectorVocabulary vocabulary = new ConnectorVocabulary(
                "connector-gmail",
                List.of(
                        new Verb(
                                "list",
                                Verb.Mode.READ,
                                "List messages in a folder.",
                                Map.of("type", "object", "properties", Map.of("folder", Map.of("type", "string"))),
                                "Array of message headers."),
                        new Verb(
                                "send",
                                Verb.Mode.WRITE,
                                "Send an email.",
                                Map.of("type", "object"),
                                "The sent message's provider ID.")));

        String json = mapper.writeValueAsString(vocabulary);
        ConnectorVocabulary roundTripped = mapper.readValue(json, ConnectorVocabulary.class);

        assertEquals("connector-gmail", roundTripped.getConnectorId());
        assertEquals(2, roundTripped.getVerbs().size());
        assertEquals(Verb.Mode.READ, roundTripped.getVerbs().get(0).getMode());
        assertEquals(Verb.Mode.WRITE, roundTripped.getVerbs().get(1).getMode());
        assertEquals("object", roundTripped.getVerbs().get(0).getParams().get("type"));
    }

    @Test
    void connectorInvokeRequestRoundTripsWithoutConfirmationToken() throws Exception {
        ConnectorInvokeRequest request = new ConnectorInvokeRequest(
                UUID.randomUUID(),
                "orchestrator",
                "list",
                Map.of("folder", "inbox"),
                null);

        String json = mapper.writeValueAsString(request);
        ConnectorInvokeRequest roundTripped = mapper.readValue(json, ConnectorInvokeRequest.class);

        assertEquals("orchestrator", roundTripped.getCaller());
        assertEquals("list", roundTripped.getVerb());
        assertEquals("inbox", roundTripped.getParams().get("folder"));
        assertNull(roundTripped.getConfirmationToken());
    }

    @Test
    void connectorInvokeRequestRoundTripsWithConfirmationToken() throws Exception {
        ConnectorInvokeRequest request = new ConnectorInvokeRequest(
                UUID.randomUUID(),
                "orchestrator",
                "send",
                Map.of("to", "owner@example.com"),
                "signed-token-abc");

        String json = mapper.writeValueAsString(request);
        ConnectorInvokeRequest roundTripped = mapper.readValue(json, ConnectorInvokeRequest.class);

        assertEquals("signed-token-abc", roundTripped.getConfirmationToken());
    }

    @Test
    void connectorInvokeResponseRoundTripsOkStatus() throws Exception {
        ConnectorInvokeResponse response = new ConnectorInvokeResponse(
                UUID.randomUUID(),
                ConnectorInvokeResponse.Status.OK,
                Map.of("messageId", "abc-123"),
                null);

        String json = mapper.writeValueAsString(response);
        ConnectorInvokeResponse roundTripped = mapper.readValue(json, ConnectorInvokeResponse.class);

        assertEquals(ConnectorInvokeResponse.Status.OK, roundTripped.getStatus());
        assertEquals("abc-123", roundTripped.getResult().get("messageId"));
        assertNull(roundTripped.getReason());
    }

    @Test
    void connectorInvokeResponseRoundTripsRefusedStatus() throws Exception {
        ConnectorInvokeResponse response = new ConnectorInvokeResponse(
                UUID.randomUUID(),
                ConnectorInvokeResponse.Status.REFUSED,
                null,
                "verb 'delete' is not in this connector's declared vocabulary");

        String json = mapper.writeValueAsString(response);
        ConnectorInvokeResponse roundTripped = mapper.readValue(json, ConnectorInvokeResponse.class);

        assertEquals(ConnectorInvokeResponse.Status.REFUSED, roundTripped.getStatus());
        assertEquals(
                "verb 'delete' is not in this connector's declared vocabulary",
                roundTripped.getReason());
    }
}

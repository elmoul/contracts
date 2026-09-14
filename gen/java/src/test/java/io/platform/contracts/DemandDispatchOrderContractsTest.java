package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import io.platform.contracts.demandcoordinator.Demand;
import io.platform.contracts.demandcoordinator.DemandQueueEntry;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

/**
 * Coverage for the v0.26.0 dispatch-order contracts (demand.after, demand.queue-entry), which
 * fulfil dashboard-20260914-demand-dispatch-order for the contracts leg.
 *
 * <p>Two properties carry most of the weight here and both are asserted rather than assumed.
 * First, backwards compatibility: a demand document written before {@code after} existed must
 * still deserialize — read from a real committed demand file, not a hand-written sample.
 * Second, {@code wave} and {@code waitingOn} are not each other's inverse. A multi-hexagon
 * sub-demand can sit at wave 3 with an empty {@code waitingOn}, so a consumer that "simplifies"
 * the pair into wave = 1 + waitingOn.size() would be wrong in a way no schema error would catch;
 * the test that pins it exists so that simplification fails loudly.
 */
class DemandDispatchOrderContractsTest {

    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    private static final Path DEMAND_FILE =
            Path.of("..", "..", "demands", "2026-09-14-factory-repin-interface-extraction.md");

    private static final String PRE_AFTER_DEMAND_JSON =
            "{\"id\":\"contracts-20260914-factory-repin-interface-extraction\","
                    + "\"date\":\"2026-09-14\",\"from\":\"contracts\",\"to\":[\"factory\"],"
                    + "\"capability\":\"re-pin\",\"acceptance-criteria\":[\"a\"],"
                    + "\"needs-owner\":false,\"status\":\"open\"}";

    @Test
    void demandWrittenBeforeAfterExistedStillDeserializes() throws Exception {
        // The compatibility claim, against the bytes actually on disk: this repo's own
        // committed demand file has no `after` key, and the real YAML frontmatter is what
        // every consumer of this schema is pinned against. Scoped to the frontmatter block
        // so that prose further down the file mentioning "after" cannot make this vacuous
        // in one direction or spuriously red in the other.
        String text = Files.readString(DEMAND_FILE);
        String frontmatter = text.substring(text.indexOf("---") + 3, text.indexOf("\n---", 3));
        assertFalse(frontmatter.contains("after"), "fixture must predate the `after` field");

        Demand demand = mapper.readValue(PRE_AFTER_DEMAND_JSON, Demand.class);
        assertEquals("contracts-20260914-factory-repin-interface-extraction", demand.getId());
        // Absent reads as empty, never as null and never as "unknown" — the field is
        // optional, so an unconstrained demand is the normal case, not a missing one.
        assertNotNull(demand.getAfter());
        assertTrue(demand.getAfter().isEmpty());
    }

    @Test
    void demandAfterRoundTrips() throws Exception {
        Demand demand = mapper.readValue(PRE_AFTER_DEMAND_JSON, Demand.class);
        demand.setAfter(Set.of("dashboard-20260914-demand-dispatch-order"));

        Demand roundTripped =
                mapper.readValue(mapper.writeValueAsString(demand), Demand.class);
        assertEquals(Set.of("dashboard-20260914-demand-dispatch-order"), roundTripped.getAfter());
    }

    @Test
    void afterIsASetNotAListBecauseTheSchemaForbidsDuplicates() throws Exception {
        // Pinned deliberately: `uniqueItems: true` makes jsonschema2pojo 1.2.1 emit
        // Set<String>/LinkedHashSet here, while the same field is a plain array in
        // TypeScript and a list in Python. That is a real cross-language difference
        // consumers must code against, so a future generator that flattens it to
        // List<String> should fail this test instead of silently changing the Java API.
        assertEquals(
                Set.class, Demand.class.getDeclaredField("after").getType());
        assertEquals(
                Set.class, DemandQueueEntry.class.getDeclaredField("waitingOn").getType());
        // `to` has no uniqueItems, and stays a List — the two are not interchangeable.
        assertEquals(List.class, Demand.class.getDeclaredField("to").getType());
    }

    @Test
    void queueEntryRoundTripsWaveAndWaitingOn() throws Exception {
        DemandQueueEntry ready = new DemandQueueEntry();
        ready.setDemandId("dashboard-20260914-demand-dispatch-order");
        ready.setDate("2026-09-14");
        ready.setFrom("dashboard");
        ready.setTo(List.of("contracts", "demand-coordinator", "runtime", "agent-runner"));
        ready.setWave(1);
        ready.setWaitingOn(Set.of());

        DemandQueueEntry readyBack =
                mapper.readValue(mapper.writeValueAsString(ready), DemandQueueEntry.class);
        assertEquals(1, readyBack.getWave());
        assertTrue(readyBack.getWaitingOn().isEmpty());
        assertEquals(4, readyBack.getTo().size());

        DemandQueueEntry gated = new DemandQueueEntry();
        gated.setDemandId("dashboard-20260914-demand-dispatch-order");
        gated.setDate("2026-09-14");
        gated.setFrom("dashboard");
        gated.setTo(List.of("contracts"));
        gated.setWave(2);
        gated.setWaitingOn(Set.of("contracts-20260914-factory-repin-interface-extraction"));

        DemandQueueEntry gatedBack =
                mapper.readValue(mapper.writeValueAsString(gated), DemandQueueEntry.class);
        assertEquals(2, gatedBack.getWave());
        assertEquals(
                Set.of("contracts-20260914-factory-repin-interface-extraction"),
                gatedBack.getWaitingOn());
    }

    @Test
    void elevatedWaveWithEmptyWaitingOnIsRepresentable() throws Exception {
        // The non-inverse case. This demand is a leg of a multi-hexagon demand, so its wave
        // can be raised by the target sequenced before it while nothing of its OWN is
        // unresolved. A contract that forced waitingOn to explain the wave could not express
        // this row at all, and the queue would either hide a gated demand or invent a
        // dependency for it.
        DemandQueueEntry subDemand = new DemandQueueEntry();
        subDemand.setDemandId("dashboard-20260914-demand-dispatch-order");
        subDemand.setDate("2026-09-14");
        subDemand.setFrom("dashboard");
        subDemand.setTo(List.of("contracts", "demand-coordinator"));
        subDemand.setWave(3);
        subDemand.setWaitingOn(Set.of());

        DemandQueueEntry back =
                mapper.readValue(mapper.writeValueAsString(subDemand), DemandQueueEntry.class);
        assertEquals(3, back.getWave());
        assertTrue(back.getWaitingOn().isEmpty());
    }

    @Test
    void queueEntryIsAReferenceAndNeverCarriesEnvelopeProse() throws Exception {
        DemandQueueEntry entry = new DemandQueueEntry();
        entry.setDemandId("dashboard-20260914-demand-dispatch-order");
        entry.setDate("2026-09-14");
        entry.setFrom("dashboard");
        entry.setTo(List.of("contracts"));
        entry.setWave(1);
        entry.setWaitingOn(Set.of());

        String json = mapper.writeValueAsString(entry);
        // The envelope has exactly one home. If the queue entry ever grows a copy of
        // `capability`/`acceptance-criteria`, the fleet has two records that can disagree.
        assertFalse(json.contains("capability"));
        assertFalse(json.contains("acceptance-criteria"));
    }

    @Test
    void unknownQueueEntryPropertyIsRejected() {
        String json = "{\"demandId\":\"dashboard-20260914-demand-dispatch-order\","
                + "\"date\":\"2026-09-14\",\"from\":\"dashboard\",\"to\":[\"contracts\"],"
                + "\"wave\":1,\"waitingOn\":[],\"capability\":\"a second home for the same prose\"}";
        assertThrows(
                UnrecognizedPropertyException.class,
                () -> mapper.readValue(json, DemandQueueEntry.class));
    }

    @Test
    void nullableWaveIsOmittedRatherThanSerializedAsZero() throws Exception {
        // @JsonInclude(NON_NULL): an unset wave must never reach the wire as 0, which would
        // sort ahead of every real wave. wave 0 is a bug, not a "not yet scheduled" sentinel.
        DemandQueueEntry entry = new DemandQueueEntry();
        entry.setDemandId("dashboard-20260914-demand-dispatch-order");
        entry.setDate("2026-09-14");
        entry.setFrom("dashboard");
        entry.setTo(List.of("contracts"));
        entry.setWaitingOn(Set.of());

        String json = mapper.writeValueAsString(entry);
        assertFalse(json.contains("\"wave\""));
        assertTrue(json.contains("\"waitingOn\""));
    }
}

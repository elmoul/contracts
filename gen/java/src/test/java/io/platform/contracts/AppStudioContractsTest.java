package io.platform.contracts;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException;
import io.platform.contracts.appstudio.AppMission;
import io.platform.contracts.appstudio.AppTaskPlan;
import io.platform.contracts.appstudio.GateRecord;
import io.platform.contracts.appstudio.SendBack;
import io.platform.contracts.appstudio.VerifyStep;
import io.platform.contracts.appstudio.Wave;
import io.platform.contracts.appstudio.WaveReviewNext;
import io.platform.contracts.appstudio.WorkUnit;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * Coverage for the v0.19.0 app-studio schemas (app.mission, app.task-plan).
 *
 * <p>The two headline tests deserialize the tutor genesis pilot's OWN records — the same
 * fixtures tests/validate_app_studio.py validates — rather than hand-written samples. These
 * schemas were extracted after that build proved the shapes (D066 build-then-extract), so
 * reading the real artifact is the point rather than a nicety.
 */
class AppStudioContractsTest {

    // OffsetDateTime is this repo's dateTimeType for every generated POJO, so the
    // JSR-310 module is required to (de)serialize decidedAt/recordedAt at all.
    private final ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());

    private static final Path FIXTURES =
            Path.of("..", "..", "tests", "fixtures", "app-studio");

    private String fixture(String name) throws Exception {
        return Files.readString(FIXTURES.resolve(name));
    }

    @Test
    void tutorPilotMissionDeserializesAndRoundTrips() throws Exception {
        AppMission mission = mapper.readValue(fixture("tutor-pilot-mission.json"), AppMission.class);

        assertEquals("tutor", mission.getAppName());
        assertEquals(AppMission.Class.GENESIS, mission.getClass_());
        assertEquals(AppMission.MissionStage.EXECUTING, mission.getStage());
        assertEquals(1, mission.getCurrentWave());
        assertEquals(3, mission.getGateRecords().size());
        assertTrue(mission.getSendBacks().isEmpty());
        assertTrue(mission.getRewinds().isEmpty());
        for (GateRecord record : mission.getGateRecords()) {
            assertEquals(GateRecord.Outcome.APPROVED, record.getOutcome());
            // None of the three is a wave-review, so none carries a forward choice.
            assertNull(record.getWaveReviewNext());
        }

        AppMission roundTripped =
                mapper.readValue(mapper.writeValueAsString(mission), AppMission.class);
        assertEquals(mission.getStage(), roundTripped.getStage());
        assertEquals(mission.getGateRecords().size(), roundTripped.getGateRecords().size());
    }

    @Test
    void tutorPilotPlanDeserializesAndRoundTrips() throws Exception {
        AppTaskPlan plan = mapper.readValue(fixture("tutor-pilot-plan.json"), AppTaskPlan.class);

        assertEquals("tutor", plan.getAppName());
        assertEquals(6, plan.getWaves().size());

        Wave waveOne = plan.getWaves().get(0);
        assertEquals(1, waveOne.getNumber());
        assertEquals(Wave.Status.PLANNED, waveOne.getStatus());
        assertFalse(waveOne.getOutlineOnly());
        assertEquals(8, waveOne.getUnits().size());
        // The two decision lists are distinct fields, and this plan predates the second —
        // an absent deferredToDispatch reads as empty, never as unknown.
        assertNotNull(waveOne.getDeferredToDispatch());
        assertTrue(waveOne.getDeferredToDispatch().isEmpty());

        WorkUnit first = waveOne.getUnits().get(0);
        assertEquals("T1.1", first.getId());
        assertEquals(WorkUnit.Mode.OWNER, first.getMode());
        assertEquals(WorkUnit.Status.PENDING, first.getStatus());
        assertFalse(first.getVerify().isEmpty());
        // An owner unit needs no prompt but does need a pass condition.
        assertNotNull(first.getVerify().get(0).getExpect());

        AppTaskPlan roundTripped =
                mapper.readValue(mapper.writeValueAsString(plan), AppTaskPlan.class);
        assertEquals(plan.getWaves().size(), roundTripped.getWaves().size());
        assertEquals(
                waveOne.getUnits().size(), roundTripped.getWaves().get(0).getUnits().size());
    }

    @Test
    void waveReviewApprovalCarriesTheOwnersForwardChoice() throws Exception {
        GateRecord record = new GateRecord();
        record.setGate(GateRecord.MissionGateStage.WAVE_REVIEW);
        record.setOutcome(GateRecord.Outcome.APPROVED);
        record.setNotes("wave 1 shipped; replan wave 2 before dispatching it");
        record.setWaveReviewNext(WaveReviewNext.REPLAN.value());
        record.setWave(1);

        GateRecord roundTripped =
                mapper.readValue(mapper.writeValueAsString(record), GateRecord.class);
        // Pinned deliberately: `waveReviewNext` and `abortedFrom` are nullable enums,
        // expressed in the schema as oneOf[$ref, null]. jsonschema2pojo 1.2.1 does not
        // follow a oneOf, so both land as java.lang.Object here while Python and
        // TypeScript get a proper nullable enum — see $defs/waveReviewNext in
        // schemas/app-studio/app.mission.json for why that trade was taken. Asserted
        // rather than worked around, so a future generator that DOES follow the oneOf
        // fails this test loudly instead of changing the Java API silently.
        assertEquals(WaveReviewNext.REPLAN.value(), roundTripped.getWaveReviewNext());
        assertEquals(Object.class, GateRecord.class.getDeclaredField("waveReviewNext").getType());
        assertEquals(Object.class, AppMission.class.getDeclaredField("abortedFrom").getType());
        assertEquals(3, WaveReviewNext.values().length);
    }

    @Test
    void sendBackIsItsOwnRecordTypeWithNoVerdict() throws Exception {
        SendBack sendBack = new SendBack();
        // Shared enum: jsonschema2pojo hoists the $defs/missionGateStage enum onto the first
        // type that references it, so SendBack.gate is GateRecord.MissionGateStage — one enum,
        // as the schema intends, not a per-record copy.
        sendBack.setGate(GateRecord.MissionGateStage.PLAN_GATE);
        sendBack.setNotes("this gate cannot be honestly evaluated as instrumented");
        sendBack.setWave(1);

        String json = mapper.writeValueAsString(sendBack);
        // The distinction the two lists exist to preserve: a send-back has no outcome,
        // so it can never be read back as a decision.
        assertFalse(json.contains("outcome"));
        assertEquals(2, GateRecord.Outcome.values().length);
    }

    @Test
    void unknownGateOutcomeIsRejected() {
        String json = "{\"gate\":\"plan-gate\",\"outcome\":\"send-back\",\"notes\":\"\","
                + "\"decidedAt\":\"2026-08-04T07:00:00Z\"}";
        assertThrows(Exception.class, () -> mapper.readValue(json, GateRecord.class));
    }

    @Test
    void unknownWorkUnitPropertyIsRejected() {
        String json = "{\"id\":\"T1.1\",\"title\":\"t\",\"mode\":\"agent\",\"status\":\"pending\","
                + "\"verify\":[],\"owner\":\"someone\"}";
        assertThrows(
                UnrecognizedPropertyException.class, () -> mapper.readValue(json, WorkUnit.class));
    }

    @Test
    void everyModeAndUnitStatusIsAvailable() throws Exception {
        assertEquals(4, WorkUnit.Mode.values().length);
        assertEquals(5, WorkUnit.Status.values().length);
        assertEquals(5, Wave.Status.values().length);
        assertEquals(15, AppMission.MissionStage.values().length);

        WorkUnit advisory = new WorkUnit();
        advisory.setId("T1.9");
        advisory.setTitle("Note: the kids-class template is the long pole");
        advisory.setMode(WorkUnit.Mode.ADVISORY);
        advisory.setStatus(WorkUnit.Status.PENDING);
        advisory.setVerify(List.of());

        WorkUnit roundTripped =
                mapper.readValue(mapper.writeValueAsString(advisory), WorkUnit.class);
        assertEquals(WorkUnit.Mode.ADVISORY, roundTripped.getMode());
        assertTrue(roundTripped.getVerify().isEmpty());
    }

    @Test
    void verifyStepCarriesEitherACommandOrAManualCheck() throws Exception {
        VerifyStep runnable = new VerifyStep();
        runnable.setRun("mvn -f gen/java/pom.xml test");
        runnable.setExpect("BUILD SUCCESS");

        VerifyStep manual = new VerifyStep();
        manual.setManual("The private GitHub repository named `tutor` exists.");
        manual.setExpect("The repository page loads and is marked Private.");

        VerifyStep runnableBack =
                mapper.readValue(mapper.writeValueAsString(runnable), VerifyStep.class);
        VerifyStep manualBack =
                mapper.readValue(mapper.writeValueAsString(manual), VerifyStep.class);

        assertNull(runnableBack.getManual());
        assertNull(manualBack.getRun());
        assertEquals("BUILD SUCCESS", runnableBack.getExpect());
        assertEquals(
                "The repository page loads and is marked Private.", manualBack.getExpect());
    }
}

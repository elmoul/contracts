
package io.platform.contracts.cirunner;

import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.Map;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;


/**
 * BuildResult
 * <p>
 * Async result reported by ci-runner to control-plane after a workflow run completes. Sent via HTTP POST to the control-plane build-result port once the GitHub webhook delivers the final `workflow_job` event.
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "correlationId",
    "repo",
    "ref",
    "runId",
    "status",
    "artifactRef",
    "completedAt"
})
@Generated("jsonschema2pojo")
public class BuildResult {

    /**
     * Echoed from the original BuildCommand.
     * (Required)
     * 
     */
    @JsonProperty("correlationId")
    @JsonPropertyDescription("Echoed from the original BuildCommand.")
    private String correlationId;
    /**
     * Full GitHub repository name (owner/repo).
     * (Required)
     * 
     */
    @JsonProperty("repo")
    @JsonPropertyDescription("Full GitHub repository name (owner/repo).")
    private String repo;
    /**
     * Git ref that was built.
     * (Required)
     * 
     */
    @JsonProperty("ref")
    @JsonPropertyDescription("Git ref that was built.")
    private String ref;
    /**
     * GitHub Actions workflow run ID.
     * (Required)
     * 
     */
    @JsonProperty("runId")
    @JsonPropertyDescription("GitHub Actions workflow run ID.")
    private Integer runId;
    /**
     * Terminal outcome of the build.
     * (Required)
     * 
     */
    @JsonProperty("status")
    @JsonPropertyDescription("Terminal outcome of the build.")
    private BuildResult.Status status;
    /**
     * GHCR image reference (e.g. ghcr.io/elmoul/plant-pal:sha-abc1234) if the workflow pushed an image. Absent when no image was produced.
     * 
     * 
     */
    @JsonProperty("artifactRef")
    @JsonPropertyDescription("GHCR image reference (e.g. ghcr.io/elmoul/plant-pal:sha-abc1234) if the workflow pushed an image. Absent when no image was produced.\n")
    private String artifactRef;
    /**
     * ISO-8601 timestamp of build completion (from GitHub webhook).
     * (Required)
     * 
     */
    @JsonProperty("completedAt")
    @JsonPropertyDescription("ISO-8601 timestamp of build completion (from GitHub webhook).")
    private OffsetDateTime completedAt;

    /**
     * No args constructor for use in serialization
     * 
     */
    public BuildResult() {
    }

    /**
     * 
     * @param ref
     *     Git ref that was built.
     * @param completedAt
     *     ISO-8601 timestamp of build completion (from GitHub webhook).
     * @param artifactRef
     *     GHCR image reference (e.g. ghcr.io/elmoul/plant-pal:sha-abc1234) if the workflow pushed an image. Absent when no image was produced.
     *     .
     * @param repo
     *     Full GitHub repository name (owner/repo).
     * @param correlationId
     *     Echoed from the original BuildCommand.
     * @param runId
     *     GitHub Actions workflow run ID.
     * @param status
     *     Terminal outcome of the build.
     */
    public BuildResult(String correlationId, String repo, String ref, Integer runId, BuildResult.Status status, String artifactRef, OffsetDateTime completedAt) {
        super();
        this.correlationId = correlationId;
        this.repo = repo;
        this.ref = ref;
        this.runId = runId;
        this.status = status;
        this.artifactRef = artifactRef;
        this.completedAt = completedAt;
    }

    /**
     * Echoed from the original BuildCommand.
     * (Required)
     * 
     */
    @JsonProperty("correlationId")
    public String getCorrelationId() {
        return correlationId;
    }

    /**
     * Echoed from the original BuildCommand.
     * (Required)
     * 
     */
    @JsonProperty("correlationId")
    public void setCorrelationId(String correlationId) {
        this.correlationId = correlationId;
    }

    /**
     * Full GitHub repository name (owner/repo).
     * (Required)
     * 
     */
    @JsonProperty("repo")
    public String getRepo() {
        return repo;
    }

    /**
     * Full GitHub repository name (owner/repo).
     * (Required)
     * 
     */
    @JsonProperty("repo")
    public void setRepo(String repo) {
        this.repo = repo;
    }

    /**
     * Git ref that was built.
     * (Required)
     * 
     */
    @JsonProperty("ref")
    public String getRef() {
        return ref;
    }

    /**
     * Git ref that was built.
     * (Required)
     * 
     */
    @JsonProperty("ref")
    public void setRef(String ref) {
        this.ref = ref;
    }

    /**
     * GitHub Actions workflow run ID.
     * (Required)
     * 
     */
    @JsonProperty("runId")
    public Integer getRunId() {
        return runId;
    }

    /**
     * GitHub Actions workflow run ID.
     * (Required)
     * 
     */
    @JsonProperty("runId")
    public void setRunId(Integer runId) {
        this.runId = runId;
    }

    /**
     * Terminal outcome of the build.
     * (Required)
     * 
     */
    @JsonProperty("status")
    public BuildResult.Status getStatus() {
        return status;
    }

    /**
     * Terminal outcome of the build.
     * (Required)
     * 
     */
    @JsonProperty("status")
    public void setStatus(BuildResult.Status status) {
        this.status = status;
    }

    /**
     * GHCR image reference (e.g. ghcr.io/elmoul/plant-pal:sha-abc1234) if the workflow pushed an image. Absent when no image was produced.
     * 
     * 
     */
    @JsonProperty("artifactRef")
    public String getArtifactRef() {
        return artifactRef;
    }

    /**
     * GHCR image reference (e.g. ghcr.io/elmoul/plant-pal:sha-abc1234) if the workflow pushed an image. Absent when no image was produced.
     * 
     * 
     */
    @JsonProperty("artifactRef")
    public void setArtifactRef(String artifactRef) {
        this.artifactRef = artifactRef;
    }

    /**
     * ISO-8601 timestamp of build completion (from GitHub webhook).
     * (Required)
     * 
     */
    @JsonProperty("completedAt")
    public OffsetDateTime getCompletedAt() {
        return completedAt;
    }

    /**
     * ISO-8601 timestamp of build completion (from GitHub webhook).
     * (Required)
     * 
     */
    @JsonProperty("completedAt")
    public void setCompletedAt(OffsetDateTime completedAt) {
        this.completedAt = completedAt;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(BuildResult.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("correlationId");
        sb.append('=');
        sb.append(((this.correlationId == null)?"<null>":this.correlationId));
        sb.append(',');
        sb.append("repo");
        sb.append('=');
        sb.append(((this.repo == null)?"<null>":this.repo));
        sb.append(',');
        sb.append("ref");
        sb.append('=');
        sb.append(((this.ref == null)?"<null>":this.ref));
        sb.append(',');
        sb.append("runId");
        sb.append('=');
        sb.append(((this.runId == null)?"<null>":this.runId));
        sb.append(',');
        sb.append("status");
        sb.append('=');
        sb.append(((this.status == null)?"<null>":this.status));
        sb.append(',');
        sb.append("artifactRef");
        sb.append('=');
        sb.append(((this.artifactRef == null)?"<null>":this.artifactRef));
        sb.append(',');
        sb.append("completedAt");
        sb.append('=');
        sb.append(((this.completedAt == null)?"<null>":this.completedAt));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.ref == null)? 0 :this.ref.hashCode()));
        result = ((result* 31)+((this.completedAt == null)? 0 :this.completedAt.hashCode()));
        result = ((result* 31)+((this.artifactRef == null)? 0 :this.artifactRef.hashCode()));
        result = ((result* 31)+((this.repo == null)? 0 :this.repo.hashCode()));
        result = ((result* 31)+((this.correlationId == null)? 0 :this.correlationId.hashCode()));
        result = ((result* 31)+((this.runId == null)? 0 :this.runId.hashCode()));
        result = ((result* 31)+((this.status == null)? 0 :this.status.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof BuildResult) == false) {
            return false;
        }
        BuildResult rhs = ((BuildResult) other);
        return ((((((((this.ref == rhs.ref)||((this.ref!= null)&&this.ref.equals(rhs.ref)))&&((this.completedAt == rhs.completedAt)||((this.completedAt!= null)&&this.completedAt.equals(rhs.completedAt))))&&((this.artifactRef == rhs.artifactRef)||((this.artifactRef!= null)&&this.artifactRef.equals(rhs.artifactRef))))&&((this.repo == rhs.repo)||((this.repo!= null)&&this.repo.equals(rhs.repo))))&&((this.correlationId == rhs.correlationId)||((this.correlationId!= null)&&this.correlationId.equals(rhs.correlationId))))&&((this.runId == rhs.runId)||((this.runId!= null)&&this.runId.equals(rhs.runId))))&&((this.status == rhs.status)||((this.status!= null)&&this.status.equals(rhs.status))));
    }


    /**
     * Terminal outcome of the build.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Status {

        SUCCESS("success"),
        FAILURE("failure"),
        CANCELLED("cancelled"),
        TIMED_OUT("timed_out");
        private final String value;
        private final static Map<String, BuildResult.Status> CONSTANTS = new HashMap<String, BuildResult.Status>();

        static {
            for (BuildResult.Status c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Status(String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return this.value;
        }

        @JsonValue
        public String value() {
            return this.value;
        }

        @JsonCreator
        public static BuildResult.Status fromValue(String value) {
            BuildResult.Status constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

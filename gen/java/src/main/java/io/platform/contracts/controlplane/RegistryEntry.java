
package io.platform.contracts.controlplane;

import java.net.URI;
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
 * RegistryEntry
 * <p>
 * Control plane's served record for a registered hexagon (D014) — a descriptor summary plus changing state. Populated from a repo's hexagon.descriptor frontmatter plus git/CI-sourced state.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "functionalName",
    "kind",
    "side",
    "status",
    "repoUrl",
    "version",
    "contractsPin",
    "updatedAt",
    "appId",
    "class",
    "plan"
})
@Generated("jsonschema2pojo")
public class RegistryEntry {

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("functionalName")
    private String functionalName;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("kind")
    private RegistryEntry.Kind kind;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("side")
    private RegistryEntry.Side side;
    /**
     * `suspended` exists only here — a registry action, not a repo property.
     * (Required)
     * 
     */
    @JsonProperty("status")
    @JsonPropertyDescription("`suspended` exists only here \u2014 a registry action, not a repo property.")
    private RegistryEntry.Status status;
    /**
     * Source repository URL.
     * (Required)
     * 
     */
    @JsonProperty("repoUrl")
    @JsonPropertyDescription("Source repository URL.")
    private URI repoUrl;
    /**
     * Git tag where one exists, else version+shortsha.
     * (Required)
     * 
     */
    @JsonProperty("version")
    @JsonPropertyDescription("Git tag where one exists, else version+shortsha.")
    private String version;
    /**
     * Mirror of the descriptor's contracts.pin.
     * 
     */
    @JsonProperty("contractsPin")
    @JsonPropertyDescription("Mirror of the descriptor's contracts.pin.")
    private String contractsPin;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("updatedAt")
    private OffsetDateTime updatedAt;
    /**
     * App-only. Populated when app.manifest registration arrives.
     * 
     */
    @JsonProperty("appId")
    @JsonPropertyDescription("App-only. Populated when app.manifest registration arrives.")
    private String appId;
    /**
     * App-only. D010 risk class tier, populated when app.manifest registration arrives.
     * 
     */
    @JsonProperty("class")
    @JsonPropertyDescription("App-only. D010 risk class tier, populated when app.manifest registration arrives.")
    private RegistryEntry.Class _class;
    /**
     * App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.
     * 
     */
    @JsonProperty("plan")
    @JsonPropertyDescription("App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.")
    private RegistryEntry.Plan plan;

    /**
     * No args constructor for use in serialization
     * 
     */
    public RegistryEntry() {
    }

    /**
     * 
     * @param repoUrl
     *     Source repository URL.
     * @param contractsPin
     *     Mirror of the descriptor's contracts.pin.
     * @param appId
     *     App-only. Populated when app.manifest registration arrives.
     * @param _class
     *     App-only. D010 risk class tier, populated when app.manifest registration arrives.
     * @param version
     *     Git tag where one exists, else version+shortsha.
     * @param plan
     *     App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.
     * @param status
     *     `suspended` exists only here — a registry action, not a repo property.
     */
    public RegistryEntry(String functionalName, RegistryEntry.Kind kind, RegistryEntry.Side side, RegistryEntry.Status status, URI repoUrl, String version, String contractsPin, OffsetDateTime updatedAt, String appId, RegistryEntry.Class _class, RegistryEntry.Plan plan) {
        super();
        this.functionalName = functionalName;
        this.kind = kind;
        this.side = side;
        this.status = status;
        this.repoUrl = repoUrl;
        this.version = version;
        this.contractsPin = contractsPin;
        this.updatedAt = updatedAt;
        this.appId = appId;
        this._class = _class;
        this.plan = plan;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("functionalName")
    public String getFunctionalName() {
        return functionalName;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("functionalName")
    public void setFunctionalName(String functionalName) {
        this.functionalName = functionalName;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("kind")
    public RegistryEntry.Kind getKind() {
        return kind;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("kind")
    public void setKind(RegistryEntry.Kind kind) {
        this.kind = kind;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("side")
    public RegistryEntry.Side getSide() {
        return side;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("side")
    public void setSide(RegistryEntry.Side side) {
        this.side = side;
    }

    /**
     * `suspended` exists only here — a registry action, not a repo property.
     * (Required)
     * 
     */
    @JsonProperty("status")
    public RegistryEntry.Status getStatus() {
        return status;
    }

    /**
     * `suspended` exists only here — a registry action, not a repo property.
     * (Required)
     * 
     */
    @JsonProperty("status")
    public void setStatus(RegistryEntry.Status status) {
        this.status = status;
    }

    /**
     * Source repository URL.
     * (Required)
     * 
     */
    @JsonProperty("repoUrl")
    public URI getRepoUrl() {
        return repoUrl;
    }

    /**
     * Source repository URL.
     * (Required)
     * 
     */
    @JsonProperty("repoUrl")
    public void setRepoUrl(URI repoUrl) {
        this.repoUrl = repoUrl;
    }

    /**
     * Git tag where one exists, else version+shortsha.
     * (Required)
     * 
     */
    @JsonProperty("version")
    public String getVersion() {
        return version;
    }

    /**
     * Git tag where one exists, else version+shortsha.
     * (Required)
     * 
     */
    @JsonProperty("version")
    public void setVersion(String version) {
        this.version = version;
    }

    /**
     * Mirror of the descriptor's contracts.pin.
     * 
     */
    @JsonProperty("contractsPin")
    public String getContractsPin() {
        return contractsPin;
    }

    /**
     * Mirror of the descriptor's contracts.pin.
     * 
     */
    @JsonProperty("contractsPin")
    public void setContractsPin(String contractsPin) {
        this.contractsPin = contractsPin;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("updatedAt")
    public OffsetDateTime getUpdatedAt() {
        return updatedAt;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("updatedAt")
    public void setUpdatedAt(OffsetDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    /**
     * App-only. Populated when app.manifest registration arrives.
     * 
     */
    @JsonProperty("appId")
    public String getAppId() {
        return appId;
    }

    /**
     * App-only. Populated when app.manifest registration arrives.
     * 
     */
    @JsonProperty("appId")
    public void setAppId(String appId) {
        this.appId = appId;
    }

    /**
     * App-only. D010 risk class tier, populated when app.manifest registration arrives.
     * 
     */
    @JsonProperty("class")
    public RegistryEntry.Class getClass_() {
        return _class;
    }

    /**
     * App-only. D010 risk class tier, populated when app.manifest registration arrives.
     * 
     */
    @JsonProperty("class")
    public void setClass_(RegistryEntry.Class _class) {
        this._class = _class;
    }

    /**
     * App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.
     * 
     */
    @JsonProperty("plan")
    public RegistryEntry.Plan getPlan() {
        return plan;
    }

    /**
     * App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.
     * 
     */
    @JsonProperty("plan")
    public void setPlan(RegistryEntry.Plan plan) {
        this.plan = plan;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(RegistryEntry.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("functionalName");
        sb.append('=');
        sb.append(((this.functionalName == null)?"<null>":this.functionalName));
        sb.append(',');
        sb.append("kind");
        sb.append('=');
        sb.append(((this.kind == null)?"<null>":this.kind));
        sb.append(',');
        sb.append("side");
        sb.append('=');
        sb.append(((this.side == null)?"<null>":this.side));
        sb.append(',');
        sb.append("status");
        sb.append('=');
        sb.append(((this.status == null)?"<null>":this.status));
        sb.append(',');
        sb.append("repoUrl");
        sb.append('=');
        sb.append(((this.repoUrl == null)?"<null>":this.repoUrl));
        sb.append(',');
        sb.append("version");
        sb.append('=');
        sb.append(((this.version == null)?"<null>":this.version));
        sb.append(',');
        sb.append("contractsPin");
        sb.append('=');
        sb.append(((this.contractsPin == null)?"<null>":this.contractsPin));
        sb.append(',');
        sb.append("updatedAt");
        sb.append('=');
        sb.append(((this.updatedAt == null)?"<null>":this.updatedAt));
        sb.append(',');
        sb.append("appId");
        sb.append('=');
        sb.append(((this.appId == null)?"<null>":this.appId));
        sb.append(',');
        sb.append("_class");
        sb.append('=');
        sb.append(((this._class == null)?"<null>":this._class));
        sb.append(',');
        sb.append("plan");
        sb.append('=');
        sb.append(((this.plan == null)?"<null>":this.plan));
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
        result = ((result* 31)+((this.repoUrl == null)? 0 :this.repoUrl.hashCode()));
        result = ((result* 31)+((this.functionalName == null)? 0 :this.functionalName.hashCode()));
        result = ((result* 31)+((this.side == null)? 0 :this.side.hashCode()));
        result = ((result* 31)+((this.contractsPin == null)? 0 :this.contractsPin.hashCode()));
        result = ((result* 31)+((this.kind == null)? 0 :this.kind.hashCode()));
        result = ((result* 31)+((this.appId == null)? 0 :this.appId.hashCode()));
        result = ((result* 31)+((this._class == null)? 0 :this._class.hashCode()));
        result = ((result* 31)+((this.version == null)? 0 :this.version.hashCode()));
        result = ((result* 31)+((this.plan == null)? 0 :this.plan.hashCode()));
        result = ((result* 31)+((this.status == null)? 0 :this.status.hashCode()));
        result = ((result* 31)+((this.updatedAt == null)? 0 :this.updatedAt.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof RegistryEntry) == false) {
            return false;
        }
        RegistryEntry rhs = ((RegistryEntry) other);
        return ((((((((((((this.repoUrl == rhs.repoUrl)||((this.repoUrl!= null)&&this.repoUrl.equals(rhs.repoUrl)))&&((this.functionalName == rhs.functionalName)||((this.functionalName!= null)&&this.functionalName.equals(rhs.functionalName))))&&((this.side == rhs.side)||((this.side!= null)&&this.side.equals(rhs.side))))&&((this.contractsPin == rhs.contractsPin)||((this.contractsPin!= null)&&this.contractsPin.equals(rhs.contractsPin))))&&((this.kind == rhs.kind)||((this.kind!= null)&&this.kind.equals(rhs.kind))))&&((this.appId == rhs.appId)||((this.appId!= null)&&this.appId.equals(rhs.appId))))&&((this._class == rhs._class)||((this._class!= null)&&this._class.equals(rhs._class))))&&((this.version == rhs.version)||((this.version!= null)&&this.version.equals(rhs.version))))&&((this.plan == rhs.plan)||((this.plan!= null)&&this.plan.equals(rhs.plan))))&&((this.status == rhs.status)||((this.status!= null)&&this.status.equals(rhs.status))))&&((this.updatedAt == rhs.updatedAt)||((this.updatedAt!= null)&&this.updatedAt.equals(rhs.updatedAt))));
    }


    /**
     * App-only. D010 risk class tier, populated when app.manifest registration arrives.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Class {

        LOW_STAKES("low-stakes"),
        HEALTH_CLASS("health-class"),
        KIDS_CLASS("kids-class");
        private final String value;
        private final static Map<String, RegistryEntry.Class> CONSTANTS = new HashMap<String, RegistryEntry.Class>();

        static {
            for (RegistryEntry.Class c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Class(String value) {
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
        public static RegistryEntry.Class fromValue(String value) {
            RegistryEntry.Class constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

    @Generated("jsonschema2pojo")
    public enum Kind {

        RUNTIME("runtime"),
        APP("app"),
        BUILDTIME("buildtime");
        private final String value;
        private final static Map<String, RegistryEntry.Kind> CONSTANTS = new HashMap<String, RegistryEntry.Kind>();

        static {
            for (RegistryEntry.Kind c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Kind(String value) {
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
        public static RegistryEntry.Kind fromValue(String value) {
            RegistryEntry.Kind constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }


    /**
     * App-only. Populated when app.manifest registration arrives; enum aligned with app.manifest's plan field.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Plan {

        FREE("free"),
        PRO("pro"),
        ENTERPRISE("enterprise");
        private final String value;
        private final static Map<String, RegistryEntry.Plan> CONSTANTS = new HashMap<String, RegistryEntry.Plan>();

        static {
            for (RegistryEntry.Plan c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Plan(String value) {
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
        public static RegistryEntry.Plan fromValue(String value) {
            RegistryEntry.Plan constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

    @Generated("jsonschema2pojo")
    public enum Side {

        HOST("host"),
        HUB("hub"),
        UI("ui"),
        SHARED("shared");
        private final String value;
        private final static Map<String, RegistryEntry.Side> CONSTANTS = new HashMap<String, RegistryEntry.Side>();

        static {
            for (RegistryEntry.Side c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Side(String value) {
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
        public static RegistryEntry.Side fromValue(String value) {
            RegistryEntry.Side constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }


    /**
     * `suspended` exists only here — a registry action, not a repo property.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Status {

        PLANNED("planned"),
        BUILDING("building"),
        ACTIVE("active"),
        SUSPENDED("suspended"),
        DEPRECATED("deprecated");
        private final String value;
        private final static Map<String, RegistryEntry.Status> CONSTANTS = new HashMap<String, RegistryEntry.Status>();

        static {
            for (RegistryEntry.Status c: values()) {
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
        public static RegistryEntry.Status fromValue(String value) {
            RegistryEntry.Status constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

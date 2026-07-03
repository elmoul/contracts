
package io.platform.contracts.controlplane;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;


/**
 * HexagonDescriptor
 * <p>
 * Machine-readable schema for the YAML frontmatter block every repo carries at the top of its HEXAGON.md (D013). Describes stable identity/structure only — deliberately no `version` field (hand-edited versions go stale); changing state lives in `registry.entry`, sourced from git/CI. Also deliberately omits `consumedBy` (derived by control-plane by inverting `deps` across the fleet) and `ports` (deferred — `deps` + `contracts.used` are the machine projection of the port tables; prose keeps the rest).
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "functionalName",
    "kind",
    "side",
    "status",
    "class",
    "spec",
    "decisions",
    "deps",
    "infra",
    "contracts"
})
@Generated("jsonschema2pojo")
public class HexagonDescriptor {

    /**
     * Functional name of the repo — no theme words (D002). Same shape as app.manifest's name.
     * (Required)
     * 
     */
    @JsonProperty("functionalName")
    @JsonPropertyDescription("Functional name of the repo \u2014 no theme words (D002). Same shape as app.manifest's name.")
    private String functionalName;
    /**
     * What this repo is: a runtime hexagon, a product app (D009), or a buildtime tool.
     * (Required)
     * 
     */
    @JsonProperty("kind")
    @JsonPropertyDescription("What this repo is: a runtime hexagon, a product app (D009), or a buildtime tool.")
    private HexagonDescriptor.Kind kind;
    /**
     * Which wall the repo sits on (D011). `ui` is the side whose repos the theme-check skips — dashboard is side: ui.
     * (Required)
     * 
     */
    @JsonProperty("side")
    @JsonPropertyDescription("Which wall the repo sits on (D011). `ui` is the side whose repos the theme-check skips \u2014 dashboard is side: ui.")
    private HexagonDescriptor.Side side;
    /**
     * Repo lifecycle state.
     * (Required)
     * 
     */
    @JsonProperty("status")
    @JsonPropertyDescription("Repo lifecycle state.")
    private HexagonDescriptor.Status status;
    /**
     * D010 risk class tier. Meaningful only when kind: app; the schema stays permissive here — policy-level enforcement (e.g. "apps must have class") belongs to the conventions validator, not this schema.
     * 
     */
    @JsonProperty("class")
    @JsonPropertyDescription("D010 risk class tier. Meaningful only when kind: app; the schema stays permissive here \u2014 policy-level enforcement (e.g. \"apps must have class\") belongs to the conventions validator, not this schema.")
    private HexagonDescriptor.Class _class;
    /**
     * Vault spec filename this repo implements.
     * 
     */
    @JsonProperty("spec")
    @JsonPropertyDescription("Vault spec filename this repo implements.")
    private String spec;
    /**
     * Platform decisions (vault PLATFORM_DECISIONS.md) this repo's design follows.
     * 
     */
    @JsonProperty("decisions")
    @JsonPropertyDescription("Platform decisions (vault PLATFORM_DECISIONS.md) this repo's design follows.")
    private List<String> decisions = new ArrayList<String>();
    /**
     * Functional names of sibling platform repos this one depends on. What dependency-direction checks (hub never imported by host) read. May be empty.
     * (Required)
     * 
     */
    @JsonProperty("deps")
    @JsonPropertyDescription("Functional names of sibling platform repos this one depends on. What dependency-direction checks (hub never imported by host) read. May be empty.")
    private List<String> deps = new ArrayList<String>();
    /**
     * Non-repo dependencies, e.g. kafka, postgres.
     * 
     */
    @JsonProperty("infra")
    @JsonPropertyDescription("Non-repo dependencies, e.g. kafka, postgres.")
    private List<String> infra = new ArrayList<String>();
    /**
     * Omitted entirely by buildtime repos like contracts itself, which pin nothing.
     * 
     */
    @JsonProperty("contracts")
    @JsonPropertyDescription("Omitted entirely by buildtime repos like contracts itself, which pin nothing.")
    private Contracts contracts;

    /**
     * No args constructor for use in serialization
     * 
     */
    public HexagonDescriptor() {
    }

    /**
     * 
     * @param functionalName
     *     Functional name of the repo — no theme words (D002). Same shape as app.manifest's name.
     * @param side
     *     Which wall the repo sits on (D011). `ui` is the side whose repos the theme-check skips — dashboard is side: ui.
     * @param kind
     *     What this repo is: a runtime hexagon, a product app (D009), or a buildtime tool.
     * @param decisions
     *     Platform decisions (vault PLATFORM_DECISIONS.md) this repo's design follows.
     * @param deps
     *     Functional names of sibling platform repos this one depends on. What dependency-direction checks (hub never imported by host) read. May be empty.
     * @param _class
     *     D010 risk class tier. Meaningful only when kind: app; the schema stays permissive here — policy-level enforcement (e.g. "apps must have class") belongs to the conventions validator, not this schema.
     * @param infra
     *     Non-repo dependencies, e.g. kafka, postgres.
     * @param contracts
     *     Omitted entirely by buildtime repos like contracts itself, which pin nothing.
     * @param spec
     *     Vault spec filename this repo implements.
     * @param status
     *     Repo lifecycle state.
     */
    public HexagonDescriptor(String functionalName, HexagonDescriptor.Kind kind, HexagonDescriptor.Side side, HexagonDescriptor.Status status, HexagonDescriptor.Class _class, String spec, List<String> decisions, List<String> deps, List<String> infra, Contracts contracts) {
        super();
        this.functionalName = functionalName;
        this.kind = kind;
        this.side = side;
        this.status = status;
        this._class = _class;
        this.spec = spec;
        this.decisions = decisions;
        this.deps = deps;
        this.infra = infra;
        this.contracts = contracts;
    }

    /**
     * Functional name of the repo — no theme words (D002). Same shape as app.manifest's name.
     * (Required)
     * 
     */
    @JsonProperty("functionalName")
    public String getFunctionalName() {
        return functionalName;
    }

    /**
     * Functional name of the repo — no theme words (D002). Same shape as app.manifest's name.
     * (Required)
     * 
     */
    @JsonProperty("functionalName")
    public void setFunctionalName(String functionalName) {
        this.functionalName = functionalName;
    }

    /**
     * What this repo is: a runtime hexagon, a product app (D009), or a buildtime tool.
     * (Required)
     * 
     */
    @JsonProperty("kind")
    public HexagonDescriptor.Kind getKind() {
        return kind;
    }

    /**
     * What this repo is: a runtime hexagon, a product app (D009), or a buildtime tool.
     * (Required)
     * 
     */
    @JsonProperty("kind")
    public void setKind(HexagonDescriptor.Kind kind) {
        this.kind = kind;
    }

    /**
     * Which wall the repo sits on (D011). `ui` is the side whose repos the theme-check skips — dashboard is side: ui.
     * (Required)
     * 
     */
    @JsonProperty("side")
    public HexagonDescriptor.Side getSide() {
        return side;
    }

    /**
     * Which wall the repo sits on (D011). `ui` is the side whose repos the theme-check skips — dashboard is side: ui.
     * (Required)
     * 
     */
    @JsonProperty("side")
    public void setSide(HexagonDescriptor.Side side) {
        this.side = side;
    }

    /**
     * Repo lifecycle state.
     * (Required)
     * 
     */
    @JsonProperty("status")
    public HexagonDescriptor.Status getStatus() {
        return status;
    }

    /**
     * Repo lifecycle state.
     * (Required)
     * 
     */
    @JsonProperty("status")
    public void setStatus(HexagonDescriptor.Status status) {
        this.status = status;
    }

    /**
     * D010 risk class tier. Meaningful only when kind: app; the schema stays permissive here — policy-level enforcement (e.g. "apps must have class") belongs to the conventions validator, not this schema.
     * 
     */
    @JsonProperty("class")
    public HexagonDescriptor.Class getClass_() {
        return _class;
    }

    /**
     * D010 risk class tier. Meaningful only when kind: app; the schema stays permissive here — policy-level enforcement (e.g. "apps must have class") belongs to the conventions validator, not this schema.
     * 
     */
    @JsonProperty("class")
    public void setClass_(HexagonDescriptor.Class _class) {
        this._class = _class;
    }

    /**
     * Vault spec filename this repo implements.
     * 
     */
    @JsonProperty("spec")
    public String getSpec() {
        return spec;
    }

    /**
     * Vault spec filename this repo implements.
     * 
     */
    @JsonProperty("spec")
    public void setSpec(String spec) {
        this.spec = spec;
    }

    /**
     * Platform decisions (vault PLATFORM_DECISIONS.md) this repo's design follows.
     * 
     */
    @JsonProperty("decisions")
    public List<String> getDecisions() {
        return decisions;
    }

    /**
     * Platform decisions (vault PLATFORM_DECISIONS.md) this repo's design follows.
     * 
     */
    @JsonProperty("decisions")
    public void setDecisions(List<String> decisions) {
        this.decisions = decisions;
    }

    /**
     * Functional names of sibling platform repos this one depends on. What dependency-direction checks (hub never imported by host) read. May be empty.
     * (Required)
     * 
     */
    @JsonProperty("deps")
    public List<String> getDeps() {
        return deps;
    }

    /**
     * Functional names of sibling platform repos this one depends on. What dependency-direction checks (hub never imported by host) read. May be empty.
     * (Required)
     * 
     */
    @JsonProperty("deps")
    public void setDeps(List<String> deps) {
        this.deps = deps;
    }

    /**
     * Non-repo dependencies, e.g. kafka, postgres.
     * 
     */
    @JsonProperty("infra")
    public List<String> getInfra() {
        return infra;
    }

    /**
     * Non-repo dependencies, e.g. kafka, postgres.
     * 
     */
    @JsonProperty("infra")
    public void setInfra(List<String> infra) {
        this.infra = infra;
    }

    /**
     * Omitted entirely by buildtime repos like contracts itself, which pin nothing.
     * 
     */
    @JsonProperty("contracts")
    public Contracts getContracts() {
        return contracts;
    }

    /**
     * Omitted entirely by buildtime repos like contracts itself, which pin nothing.
     * 
     */
    @JsonProperty("contracts")
    public void setContracts(Contracts contracts) {
        this.contracts = contracts;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(HexagonDescriptor.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
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
        sb.append("_class");
        sb.append('=');
        sb.append(((this._class == null)?"<null>":this._class));
        sb.append(',');
        sb.append("spec");
        sb.append('=');
        sb.append(((this.spec == null)?"<null>":this.spec));
        sb.append(',');
        sb.append("decisions");
        sb.append('=');
        sb.append(((this.decisions == null)?"<null>":this.decisions));
        sb.append(',');
        sb.append("deps");
        sb.append('=');
        sb.append(((this.deps == null)?"<null>":this.deps));
        sb.append(',');
        sb.append("infra");
        sb.append('=');
        sb.append(((this.infra == null)?"<null>":this.infra));
        sb.append(',');
        sb.append("contracts");
        sb.append('=');
        sb.append(((this.contracts == null)?"<null>":this.contracts));
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
        result = ((result* 31)+((this.functionalName == null)? 0 :this.functionalName.hashCode()));
        result = ((result* 31)+((this.side == null)? 0 :this.side.hashCode()));
        result = ((result* 31)+((this.kind == null)? 0 :this.kind.hashCode()));
        result = ((result* 31)+((this.decisions == null)? 0 :this.decisions.hashCode()));
        result = ((result* 31)+((this.deps == null)? 0 :this.deps.hashCode()));
        result = ((result* 31)+((this._class == null)? 0 :this._class.hashCode()));
        result = ((result* 31)+((this.infra == null)? 0 :this.infra.hashCode()));
        result = ((result* 31)+((this.contracts == null)? 0 :this.contracts.hashCode()));
        result = ((result* 31)+((this.spec == null)? 0 :this.spec.hashCode()));
        result = ((result* 31)+((this.status == null)? 0 :this.status.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof HexagonDescriptor) == false) {
            return false;
        }
        HexagonDescriptor rhs = ((HexagonDescriptor) other);
        return (((((((((((this.functionalName == rhs.functionalName)||((this.functionalName!= null)&&this.functionalName.equals(rhs.functionalName)))&&((this.side == rhs.side)||((this.side!= null)&&this.side.equals(rhs.side))))&&((this.kind == rhs.kind)||((this.kind!= null)&&this.kind.equals(rhs.kind))))&&((this.decisions == rhs.decisions)||((this.decisions!= null)&&this.decisions.equals(rhs.decisions))))&&((this.deps == rhs.deps)||((this.deps!= null)&&this.deps.equals(rhs.deps))))&&((this._class == rhs._class)||((this._class!= null)&&this._class.equals(rhs._class))))&&((this.infra == rhs.infra)||((this.infra!= null)&&this.infra.equals(rhs.infra))))&&((this.contracts == rhs.contracts)||((this.contracts!= null)&&this.contracts.equals(rhs.contracts))))&&((this.spec == rhs.spec)||((this.spec!= null)&&this.spec.equals(rhs.spec))))&&((this.status == rhs.status)||((this.status!= null)&&this.status.equals(rhs.status))));
    }


    /**
     * D010 risk class tier. Meaningful only when kind: app; the schema stays permissive here — policy-level enforcement (e.g. "apps must have class") belongs to the conventions validator, not this schema.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Class {

        LOW_STAKES("low-stakes"),
        HEALTH_CLASS("health-class"),
        KIDS_CLASS("kids-class");
        private final String value;
        private final static Map<String, HexagonDescriptor.Class> CONSTANTS = new HashMap<String, HexagonDescriptor.Class>();

        static {
            for (HexagonDescriptor.Class c: values()) {
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
        public static HexagonDescriptor.Class fromValue(String value) {
            HexagonDescriptor.Class constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }


    /**
     * What this repo is: a runtime hexagon, a product app (D009), or a buildtime tool.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Kind {

        RUNTIME("runtime"),
        APP("app"),
        BUILDTIME("buildtime");
        private final String value;
        private final static Map<String, HexagonDescriptor.Kind> CONSTANTS = new HashMap<String, HexagonDescriptor.Kind>();

        static {
            for (HexagonDescriptor.Kind c: values()) {
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
        public static HexagonDescriptor.Kind fromValue(String value) {
            HexagonDescriptor.Kind constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }


    /**
     * Which wall the repo sits on (D011). `ui` is the side whose repos the theme-check skips — dashboard is side: ui.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Side {

        HOST("host"),
        HUB("hub"),
        UI("ui"),
        SHARED("shared");
        private final String value;
        private final static Map<String, HexagonDescriptor.Side> CONSTANTS = new HashMap<String, HexagonDescriptor.Side>();

        static {
            for (HexagonDescriptor.Side c: values()) {
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
        public static HexagonDescriptor.Side fromValue(String value) {
            HexagonDescriptor.Side constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }


    /**
     * Repo lifecycle state.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Status {

        PLANNED("planned"),
        BUILDING("building"),
        ACTIVE("active"),
        DEPRECATED("deprecated");
        private final String value;
        private final static Map<String, HexagonDescriptor.Status> CONSTANTS = new HashMap<String, HexagonDescriptor.Status>();

        static {
            for (HexagonDescriptor.Status c: values()) {
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
        public static HexagonDescriptor.Status fromValue(String value) {
            HexagonDescriptor.Status constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

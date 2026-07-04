
package io.platform.contracts.connector;

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
 * Verb
 * <p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "name",
    "mode",
    "description",
    "params",
    "returns"
})
@Generated("jsonschema2pojo")
public class Verb {

    /**
     * Verb name, unique within the connector.
     * (Required)
     * 
     */
    @JsonProperty("name")
    @JsonPropertyDescription("Verb name, unique within the connector.")
    private java.lang.String name;
    /**
     * Read verbs never mutate the provider. Write verbs require a valid confirmation token to succeed — enforcement is connector-side policy (spec-connectors.md §2), not expressed in this schema.
     * (Required)
     * 
     */
    @JsonProperty("mode")
    @JsonPropertyDescription("Read verbs never mutate the provider. Write verbs require a valid confirmation token to succeed \u2014 enforcement is connector-side policy (spec-connectors.md \u00a72), not expressed in this schema.")
    private Verb.Mode mode;
    /**
     * Human-readable summary of what the verb does.
     * (Required)
     * 
     */
    @JsonProperty("description")
    @JsonPropertyDescription("Human-readable summary of what the verb does.")
    private java.lang.String description;
    /**
     * JSON-Schema-style description of the verb's parameters. Deliberately permissive — this field carries whatever shape the connector author declares and is not itself validated against the JSON Schema meta-schema.
     * (Required)
     * 
     */
    @JsonProperty("params")
    @JsonPropertyDescription("JSON-Schema-style description of the verb's parameters. Deliberately permissive \u2014 this field carries whatever shape the connector author declares and is not itself validated against the JSON Schema meta-schema.")
    private Map<String, Object> params;
    /**
     * Human-readable description of what the verb returns.
     * (Required)
     * 
     */
    @JsonProperty("returns")
    @JsonPropertyDescription("Human-readable description of what the verb returns.")
    private java.lang.String returns;

    /**
     * No args constructor for use in serialization
     * 
     */
    public Verb() {
    }

    /**
     * 
     * @param mode
     *     Read verbs never mutate the provider. Write verbs require a valid confirmation token to succeed — enforcement is connector-side policy (spec-connectors.md §2), not expressed in this schema.
     * @param name
     *     Verb name, unique within the connector.
     * @param description
     *     Human-readable summary of what the verb does.
     * @param returns
     *     Human-readable description of what the verb returns.
     * @param params
     *     JSON-Schema-style description of the verb's parameters. Deliberately permissive — this field carries whatever shape the connector author declares and is not itself validated against the JSON Schema meta-schema.
     */
    public Verb(java.lang.String name, Verb.Mode mode, java.lang.String description, Map<String, Object> params, java.lang.String returns) {
        super();
        this.name = name;
        this.mode = mode;
        this.description = description;
        this.params = params;
        this.returns = returns;
    }

    /**
     * Verb name, unique within the connector.
     * (Required)
     * 
     */
    @JsonProperty("name")
    public java.lang.String getName() {
        return name;
    }

    /**
     * Verb name, unique within the connector.
     * (Required)
     * 
     */
    @JsonProperty("name")
    public void setName(java.lang.String name) {
        this.name = name;
    }

    /**
     * Read verbs never mutate the provider. Write verbs require a valid confirmation token to succeed — enforcement is connector-side policy (spec-connectors.md §2), not expressed in this schema.
     * (Required)
     * 
     */
    @JsonProperty("mode")
    public Verb.Mode getMode() {
        return mode;
    }

    /**
     * Read verbs never mutate the provider. Write verbs require a valid confirmation token to succeed — enforcement is connector-side policy (spec-connectors.md §2), not expressed in this schema.
     * (Required)
     * 
     */
    @JsonProperty("mode")
    public void setMode(Verb.Mode mode) {
        this.mode = mode;
    }

    /**
     * Human-readable summary of what the verb does.
     * (Required)
     * 
     */
    @JsonProperty("description")
    public java.lang.String getDescription() {
        return description;
    }

    /**
     * Human-readable summary of what the verb does.
     * (Required)
     * 
     */
    @JsonProperty("description")
    public void setDescription(java.lang.String description) {
        this.description = description;
    }

    /**
     * JSON-Schema-style description of the verb's parameters. Deliberately permissive — this field carries whatever shape the connector author declares and is not itself validated against the JSON Schema meta-schema.
     * (Required)
     * 
     */
    @JsonProperty("params")
    public Map<String, Object> getParams() {
        return params;
    }

    /**
     * JSON-Schema-style description of the verb's parameters. Deliberately permissive — this field carries whatever shape the connector author declares and is not itself validated against the JSON Schema meta-schema.
     * (Required)
     * 
     */
    @JsonProperty("params")
    public void setParams(Map<String, Object> params) {
        this.params = params;
    }

    /**
     * Human-readable description of what the verb returns.
     * (Required)
     * 
     */
    @JsonProperty("returns")
    public java.lang.String getReturns() {
        return returns;
    }

    /**
     * Human-readable description of what the verb returns.
     * (Required)
     * 
     */
    @JsonProperty("returns")
    public void setReturns(java.lang.String returns) {
        this.returns = returns;
    }

    @Override
    public java.lang.String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(Verb.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("name");
        sb.append('=');
        sb.append(((this.name == null)?"<null>":this.name));
        sb.append(',');
        sb.append("mode");
        sb.append('=');
        sb.append(((this.mode == null)?"<null>":this.mode));
        sb.append(',');
        sb.append("description");
        sb.append('=');
        sb.append(((this.description == null)?"<null>":this.description));
        sb.append(',');
        sb.append("params");
        sb.append('=');
        sb.append(((this.params == null)?"<null>":this.params));
        sb.append(',');
        sb.append("returns");
        sb.append('=');
        sb.append(((this.returns == null)?"<null>":this.returns));
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
        result = ((result* 31)+((this.name == null)? 0 :this.name.hashCode()));
        result = ((result* 31)+((this.mode == null)? 0 :this.mode.hashCode()));
        result = ((result* 31)+((this.description == null)? 0 :this.description.hashCode()));
        result = ((result* 31)+((this.returns == null)? 0 :this.returns.hashCode()));
        result = ((result* 31)+((this.params == null)? 0 :this.params.hashCode()));
        return result;
    }

    @Override
    public boolean equals(java.lang.Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof Verb) == false) {
            return false;
        }
        Verb rhs = ((Verb) other);
        return ((((((this.name == rhs.name)||((this.name!= null)&&this.name.equals(rhs.name)))&&((this.mode == rhs.mode)||((this.mode!= null)&&this.mode.equals(rhs.mode))))&&((this.description == rhs.description)||((this.description!= null)&&this.description.equals(rhs.description))))&&((this.returns == rhs.returns)||((this.returns!= null)&&this.returns.equals(rhs.returns))))&&((this.params == rhs.params)||((this.params!= null)&&this.params.equals(rhs.params))));
    }


    /**
     * Read verbs never mutate the provider. Write verbs require a valid confirmation token to succeed — enforcement is connector-side policy (spec-connectors.md §2), not expressed in this schema.
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Mode {

        READ("read"),
        WRITE("write");
        private final java.lang.String value;
        private final static Map<java.lang.String, Verb.Mode> CONSTANTS = new HashMap<java.lang.String, Verb.Mode>();

        static {
            for (Verb.Mode c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Mode(java.lang.String value) {
            this.value = value;
        }

        @Override
        public java.lang.String toString() {
            return this.value;
        }

        @JsonValue
        public java.lang.String value() {
            return this.value;
        }

        @JsonCreator
        public static Verb.Mode fromValue(java.lang.String value) {
            Verb.Mode constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

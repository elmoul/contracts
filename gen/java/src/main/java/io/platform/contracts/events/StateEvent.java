
package io.platform.contracts.events;

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
 * StateEvent
 * <p>
 * Event emitted over SSE by the state-feed (D029). Consumed by the dashboard, the 3D renderer, and the guest projection — the same schema, three renderers. The 'type' field is the discriminator.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "type",
    "timestamp"
})
@Generated("jsonschema2pojo")
public class StateEvent {

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("type")
    private StateEvent.Type type;
    /**
     * ISO-8601 timestamp when the event was produced
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    @JsonPropertyDescription("ISO-8601 timestamp when the event was produced")
    private OffsetDateTime timestamp;

    /**
     * No args constructor for use in serialization
     * 
     */
    public StateEvent() {
    }

    /**
     * 
     * @param timestamp
     *     ISO-8601 timestamp when the event was produced.
     */
    public StateEvent(StateEvent.Type type, OffsetDateTime timestamp) {
        super();
        this.type = type;
        this.timestamp = timestamp;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("type")
    public StateEvent.Type getType() {
        return type;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("type")
    public void setType(StateEvent.Type type) {
        this.type = type;
    }

    /**
     * ISO-8601 timestamp when the event was produced
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public OffsetDateTime getTimestamp() {
        return timestamp;
    }

    /**
     * ISO-8601 timestamp when the event was produced
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public void setTimestamp(OffsetDateTime timestamp) {
        this.timestamp = timestamp;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(StateEvent.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("type");
        sb.append('=');
        sb.append(((this.type == null)?"<null>":this.type));
        sb.append(',');
        sb.append("timestamp");
        sb.append('=');
        sb.append(((this.timestamp == null)?"<null>":this.timestamp));
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
        result = ((result* 31)+((this.type == null)? 0 :this.type.hashCode()));
        result = ((result* 31)+((this.timestamp == null)? 0 :this.timestamp.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof StateEvent) == false) {
            return false;
        }
        StateEvent rhs = ((StateEvent) other);
        return (((this.type == rhs.type)||((this.type!= null)&&this.type.equals(rhs.type)))&&((this.timestamp == rhs.timestamp)||((this.timestamp!= null)&&this.timestamp.equals(rhs.timestamp))));
    }

    @Generated("jsonschema2pojo")
    public enum Type {

        COMPONENT_HEALTH("component.health"),
        LOAD("load"),
        COST_TICK("cost.tick"),
        CI_RUN("ci.run"),
        APP_STATUS("app.status");
        private final String value;
        private final static Map<String, StateEvent.Type> CONSTANTS = new HashMap<String, StateEvent.Type>();

        static {
            for (StateEvent.Type c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Type(String value) {
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
        public static StateEvent.Type fromValue(String value) {
            StateEvent.Type constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

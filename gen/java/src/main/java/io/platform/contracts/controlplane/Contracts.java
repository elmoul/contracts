
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
 * Omitted entirely by buildtime repos like contracts itself, which pin nothing.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "pin",
    "binding",
    "used"
})
@Generated("jsonschema2pojo")
public class Contracts {

    /**
     * Git tag of contracts checked out.
     * (Required)
     * 
     */
    @JsonProperty("pin")
    @JsonPropertyDescription("Git tag of contracts checked out.")
    private String pin;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("binding")
    private Contracts.Binding binding;
    /**
     * Per-contract names consumed, not per-repo — contracts version independently and the D015 rebuild set is computed per contract from this field.
     * (Required)
     * 
     */
    @JsonProperty("used")
    @JsonPropertyDescription("Per-contract names consumed, not per-repo \u2014 contracts version independently and the D015 rebuild set is computed per contract from this field.")
    private List<String> used = new ArrayList<String>();

    /**
     * No args constructor for use in serialization
     * 
     */
    public Contracts() {
    }

    /**
     * 
     * @param pin
     *     Git tag of contracts checked out.
     * @param used
     *     Per-contract names consumed, not per-repo — contracts version independently and the D015 rebuild set is computed per contract from this field.
     */
    public Contracts(String pin, Contracts.Binding binding, List<String> used) {
        super();
        this.pin = pin;
        this.binding = binding;
        this.used = used;
    }

    /**
     * Git tag of contracts checked out.
     * (Required)
     * 
     */
    @JsonProperty("pin")
    public String getPin() {
        return pin;
    }

    /**
     * Git tag of contracts checked out.
     * (Required)
     * 
     */
    @JsonProperty("pin")
    public void setPin(String pin) {
        this.pin = pin;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("binding")
    public Contracts.Binding getBinding() {
        return binding;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("binding")
    public void setBinding(Contracts.Binding binding) {
        this.binding = binding;
    }

    /**
     * Per-contract names consumed, not per-repo — contracts version independently and the D015 rebuild set is computed per contract from this field.
     * (Required)
     * 
     */
    @JsonProperty("used")
    public List<String> getUsed() {
        return used;
    }

    /**
     * Per-contract names consumed, not per-repo — contracts version independently and the D015 rebuild set is computed per contract from this field.
     * (Required)
     * 
     */
    @JsonProperty("used")
    public void setUsed(List<String> used) {
        this.used = used;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(Contracts.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("pin");
        sb.append('=');
        sb.append(((this.pin == null)?"<null>":this.pin));
        sb.append(',');
        sb.append("binding");
        sb.append('=');
        sb.append(((this.binding == null)?"<null>":this.binding));
        sb.append(',');
        sb.append("used");
        sb.append('=');
        sb.append(((this.used == null)?"<null>":this.used));
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
        result = ((result* 31)+((this.pin == null)? 0 :this.pin.hashCode()));
        result = ((result* 31)+((this.binding == null)? 0 :this.binding.hashCode()));
        result = ((result* 31)+((this.used == null)? 0 :this.used.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof Contracts) == false) {
            return false;
        }
        Contracts rhs = ((Contracts) other);
        return ((((this.pin == rhs.pin)||((this.pin!= null)&&this.pin.equals(rhs.pin)))&&((this.binding == rhs.binding)||((this.binding!= null)&&this.binding.equals(rhs.binding))))&&((this.used == rhs.used)||((this.used!= null)&&this.used.equals(rhs.used))));
    }

    @Generated("jsonschema2pojo")
    public enum Binding {

        JAVA("java"),
        TS("ts"),
        PYTHON("python");
        private final String value;
        private final static Map<String, Contracts.Binding> CONSTANTS = new HashMap<String, Contracts.Binding>();

        static {
            for (Contracts.Binding c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Binding(String value) {
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
        public static Contracts.Binding fromValue(String value) {
            Contracts.Binding constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

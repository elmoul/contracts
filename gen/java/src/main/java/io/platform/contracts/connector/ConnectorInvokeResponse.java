
package io.platform.contracts.connector;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;


/**
 * ConnectorInvokeResponse
 * <p>
 * Response envelope for one verb call against a connector (spec-connectors.md §5), correlated to a connector.invoke.request by requestId.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "requestId",
    "status",
    "result",
    "reason"
})
@Generated("jsonschema2pojo")
public class ConnectorInvokeResponse {

    /**
     * Echoes the requestId of the connector.invoke.request this responds to.
     * (Required)
     * 
     */
    @JsonProperty("requestId")
    @JsonPropertyDescription("Echoes the requestId of the connector.invoke.request this responds to.")
    private UUID requestId;
    /**
     * Outcome of the invocation. 'refused' is a first-class outcome, not an error — the connector declines a call outside its declared vocabulary, missing/invalid confirmation token, or otherwise against policy. 'error' is an unexpected failure (provider unavailable, etc.).
     * (Required)
     * 
     */
    @JsonProperty("status")
    @JsonPropertyDescription("Outcome of the invocation. 'refused' is a first-class outcome, not an error \u2014 the connector declines a call outside its declared vocabulary, missing/invalid confirmation token, or otherwise against policy. 'error' is an unexpected failure (provider unavailable, etc.).")
    private ConnectorInvokeResponse.Status status;
    /**
     * Verb-specific result payload. Present only when status is 'ok'; shape follows the invoked verb's declared returns.
     * 
     */
    @JsonProperty("result")
    @JsonPropertyDescription("Verb-specific result payload. Present only when status is 'ok'; shape follows the invoked verb's declared returns.")
    private Map<String, Object> result;
    /**
     * Human-readable explanation for a non-ok outcome. Required when status is 'refused' or 'error'; absent when status is 'ok'.
     * 
     */
    @JsonProperty("reason")
    @JsonPropertyDescription("Human-readable explanation for a non-ok outcome. Required when status is 'refused' or 'error'; absent when status is 'ok'.")
    private java.lang.String reason;

    /**
     * No args constructor for use in serialization
     * 
     */
    public ConnectorInvokeResponse() {
    }

    /**
     * 
     * @param result
     *     Verb-specific result payload. Present only when status is 'ok'; shape follows the invoked verb's declared returns.
     * @param reason
     *     Human-readable explanation for a non-ok outcome. Required when status is 'refused' or 'error'; absent when status is 'ok'.
     * @param requestId
     *     Echoes the requestId of the connector.invoke.request this responds to.
     * @param status
     *     Outcome of the invocation. 'refused' is a first-class outcome, not an error — the connector declines a call outside its declared vocabulary, missing/invalid confirmation token, or otherwise against policy. 'error' is an unexpected failure (provider unavailable, etc.).
     */
    public ConnectorInvokeResponse(UUID requestId, ConnectorInvokeResponse.Status status, Map<String, Object> result, java.lang.String reason) {
        super();
        this.requestId = requestId;
        this.status = status;
        this.result = result;
        this.reason = reason;
    }

    /**
     * Echoes the requestId of the connector.invoke.request this responds to.
     * (Required)
     * 
     */
    @JsonProperty("requestId")
    public UUID getRequestId() {
        return requestId;
    }

    /**
     * Echoes the requestId of the connector.invoke.request this responds to.
     * (Required)
     * 
     */
    @JsonProperty("requestId")
    public void setRequestId(UUID requestId) {
        this.requestId = requestId;
    }

    /**
     * Outcome of the invocation. 'refused' is a first-class outcome, not an error — the connector declines a call outside its declared vocabulary, missing/invalid confirmation token, or otherwise against policy. 'error' is an unexpected failure (provider unavailable, etc.).
     * (Required)
     * 
     */
    @JsonProperty("status")
    public ConnectorInvokeResponse.Status getStatus() {
        return status;
    }

    /**
     * Outcome of the invocation. 'refused' is a first-class outcome, not an error — the connector declines a call outside its declared vocabulary, missing/invalid confirmation token, or otherwise against policy. 'error' is an unexpected failure (provider unavailable, etc.).
     * (Required)
     * 
     */
    @JsonProperty("status")
    public void setStatus(ConnectorInvokeResponse.Status status) {
        this.status = status;
    }

    /**
     * Verb-specific result payload. Present only when status is 'ok'; shape follows the invoked verb's declared returns.
     * 
     */
    @JsonProperty("result")
    public Map<String, Object> getResult() {
        return result;
    }

    /**
     * Verb-specific result payload. Present only when status is 'ok'; shape follows the invoked verb's declared returns.
     * 
     */
    @JsonProperty("result")
    public void setResult(Map<String, Object> result) {
        this.result = result;
    }

    /**
     * Human-readable explanation for a non-ok outcome. Required when status is 'refused' or 'error'; absent when status is 'ok'.
     * 
     */
    @JsonProperty("reason")
    public java.lang.String getReason() {
        return reason;
    }

    /**
     * Human-readable explanation for a non-ok outcome. Required when status is 'refused' or 'error'; absent when status is 'ok'.
     * 
     */
    @JsonProperty("reason")
    public void setReason(java.lang.String reason) {
        this.reason = reason;
    }

    @Override
    public java.lang.String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(ConnectorInvokeResponse.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("requestId");
        sb.append('=');
        sb.append(((this.requestId == null)?"<null>":this.requestId));
        sb.append(',');
        sb.append("status");
        sb.append('=');
        sb.append(((this.status == null)?"<null>":this.status));
        sb.append(',');
        sb.append("result");
        sb.append('=');
        sb.append(((this.result == null)?"<null>":this.result));
        sb.append(',');
        sb.append("reason");
        sb.append('=');
        sb.append(((this.reason == null)?"<null>":this.reason));
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
        result = ((result* 31)+((this.result == null)? 0 :this.result.hashCode()));
        result = ((result* 31)+((this.reason == null)? 0 :this.reason.hashCode()));
        result = ((result* 31)+((this.requestId == null)? 0 :this.requestId.hashCode()));
        result = ((result* 31)+((this.status == null)? 0 :this.status.hashCode()));
        return result;
    }

    @Override
    public boolean equals(java.lang.Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof ConnectorInvokeResponse) == false) {
            return false;
        }
        ConnectorInvokeResponse rhs = ((ConnectorInvokeResponse) other);
        return (((((this.result == rhs.result)||((this.result!= null)&&this.result.equals(rhs.result)))&&((this.reason == rhs.reason)||((this.reason!= null)&&this.reason.equals(rhs.reason))))&&((this.requestId == rhs.requestId)||((this.requestId!= null)&&this.requestId.equals(rhs.requestId))))&&((this.status == rhs.status)||((this.status!= null)&&this.status.equals(rhs.status))));
    }


    /**
     * Outcome of the invocation. 'refused' is a first-class outcome, not an error — the connector declines a call outside its declared vocabulary, missing/invalid confirmation token, or otherwise against policy. 'error' is an unexpected failure (provider unavailable, etc.).
     * 
     */
    @Generated("jsonschema2pojo")
    public enum Status {

        OK("ok"),
        REFUSED("refused"),
        ERROR("error");
        private final java.lang.String value;
        private final static Map<java.lang.String, ConnectorInvokeResponse.Status> CONSTANTS = new HashMap<java.lang.String, ConnectorInvokeResponse.Status>();

        static {
            for (ConnectorInvokeResponse.Status c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        Status(java.lang.String value) {
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
        public static ConnectorInvokeResponse.Status fromValue(java.lang.String value) {
            ConnectorInvokeResponse.Status constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}

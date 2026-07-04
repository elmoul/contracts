
package io.platform.contracts.connector;

import java.util.Map;
import java.util.UUID;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * ConnectorInvokeRequest
 * <p>
 * Request envelope for one verb call against a connector (spec-connectors.md §5) — the sync in-hub call from the orchestrator (or sentinel-hub) to a connector's declared vocabulary.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "requestId",
    "caller",
    "verb",
    "params",
    "confirmationToken"
})
@Generated("jsonschema2pojo")
public class ConnectorInvokeRequest {

    /**
     * Unique identifier for this invocation, correlated with the response and the connector's local audit log.
     * (Required)
     * 
     */
    @JsonProperty("requestId")
    @JsonPropertyDescription("Unique identifier for this invocation, correlated with the response and the connector's local audit log.")
    private UUID requestId;
    /**
     * Functional name of the requesting hexagon (D002) — e.g. the orchestrator or sentinel-hub.
     * (Required)
     * 
     */
    @JsonProperty("caller")
    @JsonPropertyDescription("Functional name of the requesting hexagon (D002) \u2014 e.g. the orchestrator or sentinel-hub.")
    private java.lang.String caller;
    /**
     * Verb being invoked. Must match a verb name the target connector declares in its connector.vocabulary; anything else is refused, not an error.
     * (Required)
     * 
     */
    @JsonProperty("verb")
    @JsonPropertyDescription("Verb being invoked. Must match a verb name the target connector declares in its connector.vocabulary; anything else is refused, not an error.")
    private java.lang.String verb;
    /**
     * Verb-specific parameters, shaped per the declared verb's params schema. Deliberately permissive at this level — the connector validates against its own vocabulary.
     * (Required)
     * 
     */
    @JsonProperty("params")
    @JsonPropertyDescription("Verb-specific parameters, shaped per the declared verb's params schema. Deliberately permissive at this level \u2014 the connector validates against its own vocabulary.")
    private Map<String, Object> params;
    /**
     * Short-lived signed token binding {verb, target, content-hash}, issued by the confirmation-card flow. Write verbs require a valid token to succeed; omission or invalidity is a connector-side refusal, not enforced by this schema (spec-connectors.md §6-3).
     * 
     */
    @JsonProperty("confirmationToken")
    @JsonPropertyDescription("Short-lived signed token binding {verb, target, content-hash}, issued by the confirmation-card flow. Write verbs require a valid token to succeed; omission or invalidity is a connector-side refusal, not enforced by this schema (spec-connectors.md \u00a76-3).")
    private java.lang.String confirmationToken;

    /**
     * No args constructor for use in serialization
     * 
     */
    public ConnectorInvokeRequest() {
    }

    /**
     * 
     * @param caller
     *     Functional name of the requesting hexagon (D002) — e.g. the orchestrator or sentinel-hub.
     * @param requestId
     *     Unique identifier for this invocation, correlated with the response and the connector's local audit log.
     * @param verb
     *     Verb being invoked. Must match a verb name the target connector declares in its connector.vocabulary; anything else is refused, not an error.
     * @param confirmationToken
     *     Short-lived signed token binding {verb, target, content-hash}, issued by the confirmation-card flow. Write verbs require a valid token to succeed; omission or invalidity is a connector-side refusal, not enforced by this schema (spec-connectors.md §6-3).
     * @param params
     *     Verb-specific parameters, shaped per the declared verb's params schema. Deliberately permissive at this level — the connector validates against its own vocabulary.
     */
    public ConnectorInvokeRequest(UUID requestId, java.lang.String caller, java.lang.String verb, Map<String, Object> params, java.lang.String confirmationToken) {
        super();
        this.requestId = requestId;
        this.caller = caller;
        this.verb = verb;
        this.params = params;
        this.confirmationToken = confirmationToken;
    }

    /**
     * Unique identifier for this invocation, correlated with the response and the connector's local audit log.
     * (Required)
     * 
     */
    @JsonProperty("requestId")
    public UUID getRequestId() {
        return requestId;
    }

    /**
     * Unique identifier for this invocation, correlated with the response and the connector's local audit log.
     * (Required)
     * 
     */
    @JsonProperty("requestId")
    public void setRequestId(UUID requestId) {
        this.requestId = requestId;
    }

    /**
     * Functional name of the requesting hexagon (D002) — e.g. the orchestrator or sentinel-hub.
     * (Required)
     * 
     */
    @JsonProperty("caller")
    public java.lang.String getCaller() {
        return caller;
    }

    /**
     * Functional name of the requesting hexagon (D002) — e.g. the orchestrator or sentinel-hub.
     * (Required)
     * 
     */
    @JsonProperty("caller")
    public void setCaller(java.lang.String caller) {
        this.caller = caller;
    }

    /**
     * Verb being invoked. Must match a verb name the target connector declares in its connector.vocabulary; anything else is refused, not an error.
     * (Required)
     * 
     */
    @JsonProperty("verb")
    public java.lang.String getVerb() {
        return verb;
    }

    /**
     * Verb being invoked. Must match a verb name the target connector declares in its connector.vocabulary; anything else is refused, not an error.
     * (Required)
     * 
     */
    @JsonProperty("verb")
    public void setVerb(java.lang.String verb) {
        this.verb = verb;
    }

    /**
     * Verb-specific parameters, shaped per the declared verb's params schema. Deliberately permissive at this level — the connector validates against its own vocabulary.
     * (Required)
     * 
     */
    @JsonProperty("params")
    public Map<String, Object> getParams() {
        return params;
    }

    /**
     * Verb-specific parameters, shaped per the declared verb's params schema. Deliberately permissive at this level — the connector validates against its own vocabulary.
     * (Required)
     * 
     */
    @JsonProperty("params")
    public void setParams(Map<String, Object> params) {
        this.params = params;
    }

    /**
     * Short-lived signed token binding {verb, target, content-hash}, issued by the confirmation-card flow. Write verbs require a valid token to succeed; omission or invalidity is a connector-side refusal, not enforced by this schema (spec-connectors.md §6-3).
     * 
     */
    @JsonProperty("confirmationToken")
    public java.lang.String getConfirmationToken() {
        return confirmationToken;
    }

    /**
     * Short-lived signed token binding {verb, target, content-hash}, issued by the confirmation-card flow. Write verbs require a valid token to succeed; omission or invalidity is a connector-side refusal, not enforced by this schema (spec-connectors.md §6-3).
     * 
     */
    @JsonProperty("confirmationToken")
    public void setConfirmationToken(java.lang.String confirmationToken) {
        this.confirmationToken = confirmationToken;
    }

    @Override
    public java.lang.String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(ConnectorInvokeRequest.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("requestId");
        sb.append('=');
        sb.append(((this.requestId == null)?"<null>":this.requestId));
        sb.append(',');
        sb.append("caller");
        sb.append('=');
        sb.append(((this.caller == null)?"<null>":this.caller));
        sb.append(',');
        sb.append("verb");
        sb.append('=');
        sb.append(((this.verb == null)?"<null>":this.verb));
        sb.append(',');
        sb.append("params");
        sb.append('=');
        sb.append(((this.params == null)?"<null>":this.params));
        sb.append(',');
        sb.append("confirmationToken");
        sb.append('=');
        sb.append(((this.confirmationToken == null)?"<null>":this.confirmationToken));
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
        result = ((result* 31)+((this.verb == null)? 0 :this.verb.hashCode()));
        result = ((result* 31)+((this.confirmationToken == null)? 0 :this.confirmationToken.hashCode()));
        result = ((result* 31)+((this.caller == null)? 0 :this.caller.hashCode()));
        result = ((result* 31)+((this.params == null)? 0 :this.params.hashCode()));
        result = ((result* 31)+((this.requestId == null)? 0 :this.requestId.hashCode()));
        return result;
    }

    @Override
    public boolean equals(java.lang.Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof ConnectorInvokeRequest) == false) {
            return false;
        }
        ConnectorInvokeRequest rhs = ((ConnectorInvokeRequest) other);
        return ((((((this.verb == rhs.verb)||((this.verb!= null)&&this.verb.equals(rhs.verb)))&&((this.confirmationToken == rhs.confirmationToken)||((this.confirmationToken!= null)&&this.confirmationToken.equals(rhs.confirmationToken))))&&((this.caller == rhs.caller)||((this.caller!= null)&&this.caller.equals(rhs.caller))))&&((this.params == rhs.params)||((this.params!= null)&&this.params.equals(rhs.params))))&&((this.requestId == rhs.requestId)||((this.requestId!= null)&&this.requestId.equals(rhs.requestId))));
    }

}

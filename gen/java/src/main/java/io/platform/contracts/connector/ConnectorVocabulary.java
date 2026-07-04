
package io.platform.contracts.connector;

import java.util.ArrayList;
import java.util.List;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * ConnectorVocabulary
 * <p>
 * Machine-readable form of a connector's verb vocabulary (spec-connectors.md §2, §6-1) — mirrors what the connector's HEXAGON.md declares in prose. Lets the orchestrator discover capabilities mechanically and lets the conventions validator check 'no undeclared verbs'. A verb not listed here does not exist for that connector.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "connectorId",
    "verbs"
})
@Generated("jsonschema2pojo")
public class ConnectorVocabulary {

    /**
     * Functional name of the connector (D002). No theme words.
     * (Required)
     * 
     */
    @JsonProperty("connectorId")
    @JsonPropertyDescription("Functional name of the connector (D002). No theme words.")
    private String connectorId;
    /**
     * The connector's complete verb vocabulary. Read and write verbs are declared side by side; write verbs are distinguished only by mode, not by a separate list — the confirmation-token requirement is enforced by the connector at call time, not by this schema.
     * (Required)
     * 
     */
    @JsonProperty("verbs")
    @JsonPropertyDescription("The connector's complete verb vocabulary. Read and write verbs are declared side by side; write verbs are distinguished only by mode, not by a separate list \u2014 the confirmation-token requirement is enforced by the connector at call time, not by this schema.")
    private List<Verb> verbs = new ArrayList<Verb>();

    /**
     * No args constructor for use in serialization
     * 
     */
    public ConnectorVocabulary() {
    }

    /**
     * 
     * @param connectorId
     *     Functional name of the connector (D002). No theme words.
     * @param verbs
     *     The connector's complete verb vocabulary. Read and write verbs are declared side by side; write verbs are distinguished only by mode, not by a separate list — the confirmation-token requirement is enforced by the connector at call time, not by this schema.
     */
    public ConnectorVocabulary(String connectorId, List<Verb> verbs) {
        super();
        this.connectorId = connectorId;
        this.verbs = verbs;
    }

    /**
     * Functional name of the connector (D002). No theme words.
     * (Required)
     * 
     */
    @JsonProperty("connectorId")
    public String getConnectorId() {
        return connectorId;
    }

    /**
     * Functional name of the connector (D002). No theme words.
     * (Required)
     * 
     */
    @JsonProperty("connectorId")
    public void setConnectorId(String connectorId) {
        this.connectorId = connectorId;
    }

    /**
     * The connector's complete verb vocabulary. Read and write verbs are declared side by side; write verbs are distinguished only by mode, not by a separate list — the confirmation-token requirement is enforced by the connector at call time, not by this schema.
     * (Required)
     * 
     */
    @JsonProperty("verbs")
    public List<Verb> getVerbs() {
        return verbs;
    }

    /**
     * The connector's complete verb vocabulary. Read and write verbs are declared side by side; write verbs are distinguished only by mode, not by a separate list — the confirmation-token requirement is enforced by the connector at call time, not by this schema.
     * (Required)
     * 
     */
    @JsonProperty("verbs")
    public void setVerbs(List<Verb> verbs) {
        this.verbs = verbs;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(ConnectorVocabulary.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("connectorId");
        sb.append('=');
        sb.append(((this.connectorId == null)?"<null>":this.connectorId));
        sb.append(',');
        sb.append("verbs");
        sb.append('=');
        sb.append(((this.verbs == null)?"<null>":this.verbs));
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
        result = ((result* 31)+((this.connectorId == null)? 0 :this.connectorId.hashCode()));
        result = ((result* 31)+((this.verbs == null)? 0 :this.verbs.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof ConnectorVocabulary) == false) {
            return false;
        }
        ConnectorVocabulary rhs = ((ConnectorVocabulary) other);
        return (((this.connectorId == rhs.connectorId)||((this.connectorId!= null)&&this.connectorId.equals(rhs.connectorId)))&&((this.verbs == rhs.verbs)||((this.verbs!= null)&&this.verbs.equals(rhs.verbs))));
    }

}

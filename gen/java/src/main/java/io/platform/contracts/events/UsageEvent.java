
package io.platform.contracts.events;

import java.time.OffsetDateTime;
import java.util.UUID;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * UsageEvent
 * <p>
 * Emitted to Kafka after every AI call. The most load-bearing schema in the platform — consumed by Treasury for billing and cost enforcement (D022, D024).
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "eventId",
    "appId",
    "userId",
    "provider",
    "model",
    "tokensIn",
    "tokensOut",
    "computedCost",
    "timestamp"
})
@Generated("jsonschema2pojo")
public class UsageEvent {

    /**
     * Unique event identifier for idempotent consumption
     * (Required)
     * 
     */
    @JsonProperty("eventId")
    @JsonPropertyDescription("Unique event identifier for idempotent consumption")
    private UUID eventId;
    /**
     * Functional identifier of the app that initiated the AI call
     * (Required)
     * 
     */
    @JsonProperty("appId")
    @JsonPropertyDescription("Functional identifier of the app that initiated the AI call")
    private String appId;
    /**
     * End-user identifier within the app (attribution only; app manages its own user auth)
     * (Required)
     * 
     */
    @JsonProperty("userId")
    @JsonPropertyDescription("End-user identifier within the app (attribution only; app manages its own user auth)")
    private String userId;
    /**
     * AI provider name
     * (Required)
     * 
     */
    @JsonProperty("provider")
    @JsonPropertyDescription("AI provider name")
    private String provider;
    /**
     * Exact model identifier as returned by the provider after possible downshift
     * (Required)
     * 
     */
    @JsonProperty("model")
    @JsonPropertyDescription("Exact model identifier as returned by the provider after possible downshift")
    private String model;
    /**
     * Input tokens consumed by this call
     * (Required)
     * 
     */
    @JsonProperty("tokensIn")
    @JsonPropertyDescription("Input tokens consumed by this call")
    private Integer tokensIn;
    /**
     * Output tokens produced by this call
     * (Required)
     * 
     */
    @JsonProperty("tokensOut")
    @JsonPropertyDescription("Output tokens produced by this call")
    private Integer tokensOut;
    /**
     * Cost in USD computed by the AI gateway from provider pricing at call time
     * (Required)
     * 
     */
    @JsonProperty("computedCost")
    @JsonPropertyDescription("Cost in USD computed by the AI gateway from provider pricing at call time")
    private Double computedCost;
    /**
     * ISO-8601 timestamp of when the AI call completed
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    @JsonPropertyDescription("ISO-8601 timestamp of when the AI call completed")
    private OffsetDateTime timestamp;

    /**
     * No args constructor for use in serialization
     * 
     */
    public UsageEvent() {
    }

    /**
     * 
     * @param eventId
     *     Unique event identifier for idempotent consumption.
     * @param computedCost
     *     Cost in USD computed by the AI gateway from provider pricing at call time.
     * @param provider
     *     AI provider name.
     * @param appId
     *     Functional identifier of the app that initiated the AI call.
     * @param tokensOut
     *     Output tokens produced by this call.
     * @param model
     *     Exact model identifier as returned by the provider after possible downshift.
     * @param tokensIn
     *     Input tokens consumed by this call.
     * @param userId
     *     End-user identifier within the app (attribution only; app manages its own user auth).
     * @param timestamp
     *     ISO-8601 timestamp of when the AI call completed.
     */
    public UsageEvent(UUID eventId, String appId, String userId, String provider, String model, Integer tokensIn, Integer tokensOut, Double computedCost, OffsetDateTime timestamp) {
        super();
        this.eventId = eventId;
        this.appId = appId;
        this.userId = userId;
        this.provider = provider;
        this.model = model;
        this.tokensIn = tokensIn;
        this.tokensOut = tokensOut;
        this.computedCost = computedCost;
        this.timestamp = timestamp;
    }

    /**
     * Unique event identifier for idempotent consumption
     * (Required)
     * 
     */
    @JsonProperty("eventId")
    public UUID getEventId() {
        return eventId;
    }

    /**
     * Unique event identifier for idempotent consumption
     * (Required)
     * 
     */
    @JsonProperty("eventId")
    public void setEventId(UUID eventId) {
        this.eventId = eventId;
    }

    /**
     * Functional identifier of the app that initiated the AI call
     * (Required)
     * 
     */
    @JsonProperty("appId")
    public String getAppId() {
        return appId;
    }

    /**
     * Functional identifier of the app that initiated the AI call
     * (Required)
     * 
     */
    @JsonProperty("appId")
    public void setAppId(String appId) {
        this.appId = appId;
    }

    /**
     * End-user identifier within the app (attribution only; app manages its own user auth)
     * (Required)
     * 
     */
    @JsonProperty("userId")
    public String getUserId() {
        return userId;
    }

    /**
     * End-user identifier within the app (attribution only; app manages its own user auth)
     * (Required)
     * 
     */
    @JsonProperty("userId")
    public void setUserId(String userId) {
        this.userId = userId;
    }

    /**
     * AI provider name
     * (Required)
     * 
     */
    @JsonProperty("provider")
    public String getProvider() {
        return provider;
    }

    /**
     * AI provider name
     * (Required)
     * 
     */
    @JsonProperty("provider")
    public void setProvider(String provider) {
        this.provider = provider;
    }

    /**
     * Exact model identifier as returned by the provider after possible downshift
     * (Required)
     * 
     */
    @JsonProperty("model")
    public String getModel() {
        return model;
    }

    /**
     * Exact model identifier as returned by the provider after possible downshift
     * (Required)
     * 
     */
    @JsonProperty("model")
    public void setModel(String model) {
        this.model = model;
    }

    /**
     * Input tokens consumed by this call
     * (Required)
     * 
     */
    @JsonProperty("tokensIn")
    public Integer getTokensIn() {
        return tokensIn;
    }

    /**
     * Input tokens consumed by this call
     * (Required)
     * 
     */
    @JsonProperty("tokensIn")
    public void setTokensIn(Integer tokensIn) {
        this.tokensIn = tokensIn;
    }

    /**
     * Output tokens produced by this call
     * (Required)
     * 
     */
    @JsonProperty("tokensOut")
    public Integer getTokensOut() {
        return tokensOut;
    }

    /**
     * Output tokens produced by this call
     * (Required)
     * 
     */
    @JsonProperty("tokensOut")
    public void setTokensOut(Integer tokensOut) {
        this.tokensOut = tokensOut;
    }

    /**
     * Cost in USD computed by the AI gateway from provider pricing at call time
     * (Required)
     * 
     */
    @JsonProperty("computedCost")
    public Double getComputedCost() {
        return computedCost;
    }

    /**
     * Cost in USD computed by the AI gateway from provider pricing at call time
     * (Required)
     * 
     */
    @JsonProperty("computedCost")
    public void setComputedCost(Double computedCost) {
        this.computedCost = computedCost;
    }

    /**
     * ISO-8601 timestamp of when the AI call completed
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public OffsetDateTime getTimestamp() {
        return timestamp;
    }

    /**
     * ISO-8601 timestamp of when the AI call completed
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
        sb.append(UsageEvent.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("eventId");
        sb.append('=');
        sb.append(((this.eventId == null)?"<null>":this.eventId));
        sb.append(',');
        sb.append("appId");
        sb.append('=');
        sb.append(((this.appId == null)?"<null>":this.appId));
        sb.append(',');
        sb.append("userId");
        sb.append('=');
        sb.append(((this.userId == null)?"<null>":this.userId));
        sb.append(',');
        sb.append("provider");
        sb.append('=');
        sb.append(((this.provider == null)?"<null>":this.provider));
        sb.append(',');
        sb.append("model");
        sb.append('=');
        sb.append(((this.model == null)?"<null>":this.model));
        sb.append(',');
        sb.append("tokensIn");
        sb.append('=');
        sb.append(((this.tokensIn == null)?"<null>":this.tokensIn));
        sb.append(',');
        sb.append("tokensOut");
        sb.append('=');
        sb.append(((this.tokensOut == null)?"<null>":this.tokensOut));
        sb.append(',');
        sb.append("computedCost");
        sb.append('=');
        sb.append(((this.computedCost == null)?"<null>":this.computedCost));
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
        result = ((result* 31)+((this.eventId == null)? 0 :this.eventId.hashCode()));
        result = ((result* 31)+((this.computedCost == null)? 0 :this.computedCost.hashCode()));
        result = ((result* 31)+((this.provider == null)? 0 :this.provider.hashCode()));
        result = ((result* 31)+((this.appId == null)? 0 :this.appId.hashCode()));
        result = ((result* 31)+((this.tokensOut == null)? 0 :this.tokensOut.hashCode()));
        result = ((result* 31)+((this.model == null)? 0 :this.model.hashCode()));
        result = ((result* 31)+((this.tokensIn == null)? 0 :this.tokensIn.hashCode()));
        result = ((result* 31)+((this.userId == null)? 0 :this.userId.hashCode()));
        result = ((result* 31)+((this.timestamp == null)? 0 :this.timestamp.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof UsageEvent) == false) {
            return false;
        }
        UsageEvent rhs = ((UsageEvent) other);
        return ((((((((((this.eventId == rhs.eventId)||((this.eventId!= null)&&this.eventId.equals(rhs.eventId)))&&((this.computedCost == rhs.computedCost)||((this.computedCost!= null)&&this.computedCost.equals(rhs.computedCost))))&&((this.provider == rhs.provider)||((this.provider!= null)&&this.provider.equals(rhs.provider))))&&((this.appId == rhs.appId)||((this.appId!= null)&&this.appId.equals(rhs.appId))))&&((this.tokensOut == rhs.tokensOut)||((this.tokensOut!= null)&&this.tokensOut.equals(rhs.tokensOut))))&&((this.model == rhs.model)||((this.model!= null)&&this.model.equals(rhs.model))))&&((this.tokensIn == rhs.tokensIn)||((this.tokensIn!= null)&&this.tokensIn.equals(rhs.tokensIn))))&&((this.userId == rhs.userId)||((this.userId!= null)&&this.userId.equals(rhs.userId))))&&((this.timestamp == rhs.timestamp)||((this.timestamp!= null)&&this.timestamp.equals(rhs.timestamp))));
    }

}

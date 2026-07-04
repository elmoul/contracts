
package io.platform.contracts.events;

import java.time.OffsetDateTime;
import java.util.UUID;
import javax.annotation.processing.Generated;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * DimensionEvent
 * <p>
 * Emitted to report a change in a business dimension count (e.g. PlantPal's plant count). Consumed by Treasury for business-dimension metering and threshold enforcement (D024, D027).
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "eventId",
    "appId",
    "userId",
    "dimensionKey",
    "delta",
    "timestamp"
})
@Generated("jsonschema2pojo")
public class DimensionEvent {

    /**
     * Unique event identifier for idempotent consumption
     * (Required)
     * 
     */
    @JsonProperty("eventId")
    @JsonPropertyDescription("Unique event identifier for idempotent consumption")
    private UUID eventId;
    /**
     * Functional identifier of the app reporting the dimension change
     * (Required)
     * 
     */
    @JsonProperty("appId")
    @JsonPropertyDescription("Functional identifier of the app reporting the dimension change")
    private String appId;
    /**
     * End-user identifier within the app (attribution only)
     * (Required)
     * 
     */
    @JsonProperty("userId")
    @JsonPropertyDescription("End-user identifier within the app (attribution only)")
    private String userId;
    /**
     * Name of the business dimension being counted
     * (Required)
     * 
     */
    @JsonProperty("dimensionKey")
    @JsonPropertyDescription("Name of the business dimension being counted")
    private String dimensionKey;
    /**
     * Signed change to apply to the running count (positive on create, negative on soft-delete)
     * (Required)
     * 
     */
    @JsonProperty("delta")
    @JsonPropertyDescription("Signed change to apply to the running count (positive on create, negative on soft-delete)")
    private Integer delta;
    /**
     * ISO-8601 timestamp of when the dimension change occurred
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    @JsonPropertyDescription("ISO-8601 timestamp of when the dimension change occurred")
    private OffsetDateTime timestamp;

    /**
     * No args constructor for use in serialization
     * 
     */
    public DimensionEvent() {
    }

    /**
     * 
     * @param eventId
     *     Unique event identifier for idempotent consumption.
     * @param appId
     *     Functional identifier of the app reporting the dimension change.
     * @param delta
     *     Signed change to apply to the running count (positive on create, negative on soft-delete).
     * @param dimensionKey
     *     Name of the business dimension being counted.
     * @param userId
     *     End-user identifier within the app (attribution only).
     * @param timestamp
     *     ISO-8601 timestamp of when the dimension change occurred.
     */
    public DimensionEvent(UUID eventId, String appId, String userId, String dimensionKey, Integer delta, OffsetDateTime timestamp) {
        super();
        this.eventId = eventId;
        this.appId = appId;
        this.userId = userId;
        this.dimensionKey = dimensionKey;
        this.delta = delta;
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
     * Functional identifier of the app reporting the dimension change
     * (Required)
     * 
     */
    @JsonProperty("appId")
    public String getAppId() {
        return appId;
    }

    /**
     * Functional identifier of the app reporting the dimension change
     * (Required)
     * 
     */
    @JsonProperty("appId")
    public void setAppId(String appId) {
        this.appId = appId;
    }

    /**
     * End-user identifier within the app (attribution only)
     * (Required)
     * 
     */
    @JsonProperty("userId")
    public String getUserId() {
        return userId;
    }

    /**
     * End-user identifier within the app (attribution only)
     * (Required)
     * 
     */
    @JsonProperty("userId")
    public void setUserId(String userId) {
        this.userId = userId;
    }

    /**
     * Name of the business dimension being counted
     * (Required)
     * 
     */
    @JsonProperty("dimensionKey")
    public String getDimensionKey() {
        return dimensionKey;
    }

    /**
     * Name of the business dimension being counted
     * (Required)
     * 
     */
    @JsonProperty("dimensionKey")
    public void setDimensionKey(String dimensionKey) {
        this.dimensionKey = dimensionKey;
    }

    /**
     * Signed change to apply to the running count (positive on create, negative on soft-delete)
     * (Required)
     * 
     */
    @JsonProperty("delta")
    public Integer getDelta() {
        return delta;
    }

    /**
     * Signed change to apply to the running count (positive on create, negative on soft-delete)
     * (Required)
     * 
     */
    @JsonProperty("delta")
    public void setDelta(Integer delta) {
        this.delta = delta;
    }

    /**
     * ISO-8601 timestamp of when the dimension change occurred
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public OffsetDateTime getTimestamp() {
        return timestamp;
    }

    /**
     * ISO-8601 timestamp of when the dimension change occurred
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
        sb.append(DimensionEvent.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
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
        sb.append("dimensionKey");
        sb.append('=');
        sb.append(((this.dimensionKey == null)?"<null>":this.dimensionKey));
        sb.append(',');
        sb.append("delta");
        sb.append('=');
        sb.append(((this.delta == null)?"<null>":this.delta));
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
        result = ((result* 31)+((this.delta == null)? 0 :this.delta.hashCode()));
        result = ((result* 31)+((this.eventId == null)? 0 :this.eventId.hashCode()));
        result = ((result* 31)+((this.dimensionKey == null)? 0 :this.dimensionKey.hashCode()));
        result = ((result* 31)+((this.userId == null)? 0 :this.userId.hashCode()));
        result = ((result* 31)+((this.appId == null)? 0 :this.appId.hashCode()));
        result = ((result* 31)+((this.timestamp == null)? 0 :this.timestamp.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof DimensionEvent) == false) {
            return false;
        }
        DimensionEvent rhs = ((DimensionEvent) other);
        return (((((((this.delta == rhs.delta)||((this.delta!= null)&&this.delta.equals(rhs.delta)))&&((this.eventId == rhs.eventId)||((this.eventId!= null)&&this.eventId.equals(rhs.eventId))))&&((this.dimensionKey == rhs.dimensionKey)||((this.dimensionKey!= null)&&this.dimensionKey.equals(rhs.dimensionKey))))&&((this.userId == rhs.userId)||((this.userId!= null)&&this.userId.equals(rhs.userId))))&&((this.appId == rhs.appId)||((this.appId!= null)&&this.appId.equals(rhs.appId))))&&((this.timestamp == rhs.timestamp)||((this.timestamp!= null)&&this.timestamp.equals(rhs.timestamp))));
    }

}

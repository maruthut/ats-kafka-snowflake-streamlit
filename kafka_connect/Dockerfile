# ============================================================================
# Kafka Connect with Snowflake Connector
# ============================================================================
# This Dockerfile extends the official Confluent Kafka Connect image
# and adds the Snowflake Kafka Connector plugin
# ============================================================================

FROM confluentinc/cp-kafka-connect:7.5.0

# Install Snowflake Kafka Connector
# Download the latest version from Snowflake's Maven repository
RUN mkdir -p /usr/share/confluent-hub-components/snowflake-kafka-connector && \
    cd /tmp && \
    wget https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/2.2.0/snowflake-kafka-connector-2.2.0.jar && \
    mv snowflake-kafka-connector-2.2.0.jar /usr/share/confluent-hub-components/snowflake-kafka-connector/

# Set plugin path to include the Snowflake connector
ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components"


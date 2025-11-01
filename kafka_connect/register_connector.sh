#!/bin/bash
# Script to register Snowflake Kafka Connector
# Run this after all services are up

echo "Waiting for Kafka Connect to be ready..."
sleep 30

echo "Registering Snowflake Sink Connector..."
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @snowflake_connector_config.json

echo ""
echo "Checking connector status..."
curl -X GET http://localhost:8083/connectors/snowflake-sink-connector/status | jq .

echo ""
echo "✅ Connector registration complete!"

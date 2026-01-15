#!/bin/bash

# Setup script for Elasticsearch log retention and indexing (Task 5.3)
# This script initializes ILM policies and index templates for log management

set -e

ELASTICSEARCH_URL="${ELASTICSEARCH_HOST:-elasticsearch}:${ELASTICSEARCH_PORT:-9200}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Waiting for Elasticsearch to be ready at http://$ELASTICSEARCH_URL..."

# Wait for Elasticsearch to be healthy
for i in $(seq 1 $MAX_RETRIES); do
  if curl -s "http://$ELASTICSEARCH_URL/_cluster/health" > /dev/null 2>&1; then
    echo "Elasticsearch is ready!"
    break
  fi
  if [ $i -eq $MAX_RETRIES ]; then
    echo "ERROR: Elasticsearch failed to become ready after $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
    exit 1
  fi
  echo "Attempt $i/$MAX_RETRIES: Waiting for Elasticsearch..."
  sleep $RETRY_INTERVAL
done

echo "Setting up Index Lifecycle Management policy..."

# Create ILM policy for log retention
curl -s -X PUT "http://$ELASTICSEARCH_URL/_ilm/policy/docc2context-retention" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "docc2context-retention",
    "phases": {
      "hot": {
        "min_age": "0d",
        "actions": {
          "rollover": {
            "max_primary_store_size": "50gb",
            "max_age": "1d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "set_priority": {
            "priority": 50
          },
          "forcemerge": {
            "max_num_segments": 1
          }
        }
      },
      "cold": {
        "min_age": "90d",
        "actions": {
          "set_priority": {
            "priority": 0
          }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": {
          "delete": {}
        }
      }
    }
  }' > /dev/null

echo "✓ ILM policy created"

echo "Creating index template with retention policy..."

# Create index template with proper mappings and ILM association
curl -s -X PUT "http://$ELASTICSEARCH_URL/_index_template/docc2context" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["docc2context-*"],
    "template": {
      "settings": {
        "index.number_of_shards": 1,
        "index.number_of_replicas": 0,
        "index.lifecycle.name": "docc2context-retention",
        "index.lifecycle.rollover_alias": "docc2context"
      },
      "mappings": {
        "properties": {
          "event_type": {
            "type": "keyword"
          },
          "status": {
            "type": "keyword"
          },
          "file_name": {
            "type": "keyword"
          },
          "file_size_bytes": {
            "type": "long"
          },
          "extraction_time_seconds": {
            "type": "float"
          },
          "error_message": {
            "type": "text"
          },
          "client_ip": {
            "type": "ip"
          },
          "endpoint": {
            "type": "keyword"
          },
          "request_id": {
            "type": "keyword"
          },
          "timestamp": {
            "type": "date",
            "format": "strict_date_time"
          },
          "level": {
            "type": "keyword"
          },
          "message": {
            "type": "text"
          },
          "geoip": {
            "properties": {
              "location": {
                "type": "geo_point"
              }
            }
          }
        }
      }
    }
  }' > /dev/null

echo "✓ Index template created"

# Create initial index
curl -s -X PUT "http://$ELASTICSEARCH_URL/docc2context-$(date +%Y.%m.%d)?pretty" \
  -H "Content-Type: application/json" \
  -d '{}' > /dev/null

echo "✓ Initial index created"

echo ""
echo "Elasticsearch setup complete!"
echo ""
echo "Access points:"
echo "  - Elasticsearch API: http://$ELASTICSEARCH_URL"
echo "  - Kibana: http://kibana:5601"
echo ""
echo "Useful commands:"
echo "  - Check cluster health: curl -s http://$ELASTICSEARCH_URL/_cluster/health | jq ."
echo "  - List indices: curl -s http://$ELASTICSEARCH_URL/_cat/indices?v"
echo "  - View recent logs: curl -s http://$ELASTICSEARCH_URL/docc2context-*/_search?pretty"

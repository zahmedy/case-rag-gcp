#!/bin/bash
set -e

echo ">>> Environment: ${K_SERVICE:+Cloud Run detected} ${K_SERVICE:-Local/dev}"

# 1) Auth handling (Cloud Run uses attached SA; local can use key.json)
if [ -n "$K_SERVICE" ]; then
  echo "Cloud Run: using attached service account (no JSON key needed)."
else
  if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    if [ -f "/app/key.json" ]; then
      export GOOGLE_APPLICATION_CREDENTIALS="/app/key.json"
      echo "Local/dev: using /app/key.json"
    else
      echo "Local/dev: WARNING—no credentials; Vertex AI calls will fail."
    fi
  else
    echo "Local/dev: using GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
  fi
fi

# 2) Launch ingestion in background and write a readiness flag when finished
echo ">>> Kicking off ingestion in background..."
( python ingest.py && touch /tmp/index.ready ) &

# 3) Start Flask privately (internal only)
echo ">>> Starting Flask (internal, localhost:5001)..."
python app.py &

# 4) Start Streamlit immediately on Cloud Run’s port so health checks pass
PORT="${PORT:-8080}"
echo ">>> Launching Streamlit on port $PORT..."
exec streamlit run ui.py --server.port="$PORT" --server.address=0.0.0.0
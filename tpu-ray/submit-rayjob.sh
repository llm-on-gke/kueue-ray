
export RAY_ADDRESS="http://localhost:8265"
ray job submit --address="http://localhost:8265" \
    --working-dir . \
    -- \
    bash rayjob-script.sh
    
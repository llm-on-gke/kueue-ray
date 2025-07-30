
export RAY_ADDRESS="http://localhost:8265"
ray job submit --address="http://localhost:8265" \
    --working-dir . \
    --runtime-env=runtime-env.yaml  \
    -- bash run-job.sh
    
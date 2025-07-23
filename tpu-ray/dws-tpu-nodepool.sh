##note; GKE cluser need to be 1.32.2-gke.1652000 or later to use flex-start.

gcloud container node-pools create v6e-2-4 \
    --location=us-central1 \
    --cluster=rick-h200-gke \
    --node-locations=us-central1-b \
    --machine-type=ct6e-standard-4t \
    --tpu-topology=2x4 \
    --reservation-affinity=none \
    --enable-autoscaling \
    --enable-queued-provisioning \
    --flex-start \
    --num-nodes 0 \
    --min-nodes=0 \
    --max-nodes=2
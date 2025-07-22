# Ray on Kubernetes: A3 Mega & A3 Ultra Example

This directory contains example Kubernetes manifests and scripts for running distributed training jobs with [Ray](https://www.ray.io/) on Google Cloud's A3 Mega and A3 Ultra GPU machine types.

## Contents

- `ray-cluster-a3mega.yaml` — Ray cluster manifest for A3 Mega nodes
- `ray-cluster-a3ultra.yaml` — Ray cluster manifest for A3 Ultra nodes
- `ray-job-a3mega.yaml` — Ray job manifest for A3 Mega cluster
- `ray-job-a3ultra.yaml` — Ray job manifest for A3 Ultra cluster
- `a3ultra-runtime-env.yaml` — Ray runtime environment for A3 Ultra jobs
- `ray-job-dws-l4.yaml` — Ray job manifest for DWS L4 nodes (example)
- `train.py` — Example training script
- `nccl_allreduce_multigpu.py` — Example NCCL all-reduce script
- `dws-queues.yaml`, `dws-nodepool-l4.sh` — Supporting files for DWS queue/nodepool setup
Note: a3ultra examples from Injae's team 

## Prerequisites

- Kubernetes cluster with GPU nodes (A3 Mega or A3 Ultra)
- `kubectl` configured for your cluster
- [Ray Operator](https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/ray-cluster-operator.html) installed in your cluster
- Sufficient GPU quota for A3 Mega or A3 Ultra nodes

- for A3 Flex start cluster provisioning, you can use cluster toolkit blueprints under a3-ultra-flexstart-blueprint. Reference, https://cloud.google.com/ai-hypercomputer/docs/create/gke-ai-hypercompute on how to use cluster toolkit. 

## Usage

### 1. Deploy a Ray Cluster

**A3 Mega:**
```sh
kubectl apply -f ray-cluster-a3mega.yaml
```

**A3 Ultra:**
you may use a3-ultra-flexstart-blueprint to create GKE cluster with Flex Start and Queued Provisioning.

```sh
kubectl apply -f ray-cluster-a3ultra.yaml
```

Check the status of the Ray cluster pods:
```sh
kubectl get raycluter
```
Make sure all raycluster workers active with resources requested

### 2. Submit a Ray Job to static Ray cluster created. 
#### Instal Ray Job Cli,
```sh
pip install "ray[default]"
```
#### Port forward Ray cluster service 
```sh
kubectl port-forward svc/ray-cluster-head-svc 8265:8265
```

#### Submit Ray job 
```sh
ray job submit   --address http://localhost:8265   --runtime-env runtime-env.yaml   --working-dir .   -- python nccl_allreduce_multigpu.py
```

### 3. Create and Run Independent Rayjob with Ephemeral RayCluster inside. 
**A3 Mega:**
```sh
kubectl apply -f ray-job-a3mega.yaml
```

**A3 Ultra:**
```sh
kubectl apply -f ray-job-a3ultra.yaml
```

You can monitor the job status and logs using:
```sh
kubectl get pods -l ray.io/job-id
kubectl logs <job-pod-name>
```

### 4. Example Training Scripts

- `train.py`: Example PyTorch training script for Ray jobs.
- `nccl_allreduce_multigpu.py`: Example script for testing NCCL all-reduce across multiple GPUs.

You can modify the job manifests to point to your own scripts or adjust resource requests as needed.

### 5. Clean Up

To delete the Ray clusters and jobs:
```sh
kubectl delete -f ray-cluster-a3mega.yaml
kubectl delete -f ray-cluster-a3ultra.yaml
kubectl delete -f ray-job-a3mega.yaml
kubectl delete -f ray-job-a3ultra.yaml
```

## Notes

- In ray worker ScaleConfig setup number of GPU per worker should be 1 gpu, currently it does not support multi-gpu per worker yet, otherwise, it will alwasy use the first GPU in worker only: https://discuss.ray.io/t/when-to-use-multi-gpus-per-worker-for-a-training-job/15805

- The YAML files are templates and may require customization for your environment (e.g., image, namespace, storage, etc.).
- Ensure your cluster has the required GPU node pools and quotas.
- For more information, see the [Ray on Kubernetes documentation](https://docs.ray.io/en/latest/cluster/kubernetes/index.html).
- Ray Job Cli documentation, see the [Ray Job Cli documentation](https://docs.ray.io/en/latest/cluster/running-applications/job-submission/quickstart.html )

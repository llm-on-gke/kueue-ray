## TPU Ray Webhook, requried for multi-host 
```
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install --create-namespace --namespace cert-manager --set installCRDs=true --set global.leaderElection.namespace=cert-manager cert-manager jetstack/cert-manager
```

## Ray submit job

RAY_ADDRESS=http://localhost:8265 ray job submit --working-dir . --runtime-env=runtime-env.yaml  -- python test-tpu.py
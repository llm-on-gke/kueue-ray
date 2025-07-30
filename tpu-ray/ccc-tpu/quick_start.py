"""
 Copyright 2025 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

"""Quick Start Example

This script demonstrates how to run LoRA SFT on a toy dataset

1. Load HuggingFace Gemma2 checkpoint
2. Configure data loading and preprocessing
3. Run training across TPU/GPU devices

This script can be run on both single-host and multi-host. 
For mulit-host set up, please follow https://kithara.readthedocs.io/en/latest/scaling_with_ray.html.


Singlehost: python examples/singlehost/quick_start.py 
Multihost:  python ray/submit_job.py "python3.11 examples/multihost/ray/TPU/quick_start.py" --hf-token your_token
"""

import ray
import jax

ray.init()

num_chips_per_host = 4  # <--IMPORTANT: Use 4 for v4 and v5, 8 for v4e and v5e
num_tpu_hosts = int(ray.cluster_resources()["TPU"] / num_chips_per_host)
print(f"{num_tpu_hosts=}")

@ray.remote(resources={"TPU": num_chips_per_host})
def main():

    import subprocess

    # This is not strictly necessary, but helps to remove TPU deadlocks if you ever run into them.
    #subprocess.run(["rm", "-rf", "/tmp/libtpu_lockfile", "/tmp/tpu_logs"])

    # HuggingFace login
    from huggingface_hub import login
    import os

    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        login(token=hf_token, add_to_git_credential=False)

    # Let JAX know that we are running a distributed job
    #jax.distributed.initialize()

    # No need to change your single host job script, simply use it as it is. 
    from examples.singlehost.quick_start import run_workload

    # Run this workload on all hosts. Don't worry, we are handling 
    # all the model sharding and batch sharding for you. 
    run_workload()

ray.get([main.remote() for i in range(num_tpu_hosts)])

ray.shutdown()

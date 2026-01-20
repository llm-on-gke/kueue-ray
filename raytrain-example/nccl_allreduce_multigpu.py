import ray
import torch
import os

import ray.util.collective as collective


@ray.remote(num_gpus=8)
class Worker:
    def __init__(self):
        self.send_tensors = []
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:0'))
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:1') * 2)
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:2'))
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:3') * 2)
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:4'))
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:5') * 2)
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:6'))
        self.send_tensors.append(torch.ones((4,), dtype=torch.float32, device='cuda:7') * 2)

        self.recv = torch.zeros((4,), dtype=torch.float32, device='cuda:0')

    def setup(self, world_size, rank):
        collective.init_collective_group(world_size, rank, "nccl", "177")
        return True

    def compute(self):
        collective.allreduce_multigpu(self.send_tensors, "177")
        
        cpu_tensors = [t.cpu() for t in self.send_tensors]

        return (
            cpu_tensors,
            self.send_tensors[0].device,
            self.send_tensors[1].device,
            self.send_tensors[2].device,
            self.send_tensors[3].device,
            self.send_tensors[4].device,
            self.send_tensors[5].device,
            self.send_tensors[6].device,
            self.send_tensors[7].device,
        )

    def destroy(self):
        collective.destroy_collective_group("177")


if __name__ == "__main__":
    ray.init(address="auto")

    num_workers = int(os.getenv("NUM_WORKERS", "1"))
    workers = []
    init_rets = []

    for i in range(num_workers):
        w = Worker.remote()
        workers.append(w)
        init_rets.append(w.setup.remote(num_workers, i))
    
    ray.get(init_rets)
    print("Collective groups initialized.")

    results = ray.get([w.compute.remote() for w in workers])
    
    print("\n--- Allreduce Results ---")
    for i, (tensors_list, *devices) in enumerate(results):
        print(f"Worker {i} results:")
        for j, tensor in enumerate(tensors_list):
            print(f"  Tensor {j} (originally on {devices[j]}): {tensor.numpy()}") 

    ray.get([w.destroy.remote() for w in workers])
    print("\nCollective groups destroyed.")

    ray.shutdown()

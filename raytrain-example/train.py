# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# NOTE: this file was inspired from https://github.com/ray-project/kuberay/blob/master/ray-operator/config/samples/pytorch-mnist/ray_train_pytorch_mnist.py

import os
from typing import Dict
from filelock import FileLock
from tqdm import tqdm

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.transforms import Normalize, ToTensor

import ray.train
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer


def get_dataloaders(batch_size):
    # Transform to normalize the input images
    transform = transforms.Compose([ToTensor(), Normalize((0.5,), (0.5,))])

    with FileLock(os.path.expanduser("~/data.lock")):
        # Download training data from open datasets
        training_data = datasets.FashionMNIST(
            root="~/data",
            train=True,
            download=True,
            transform=transform,
        )

        # Download test data from open datasets
        test_data = datasets.FashionMNIST(
            root="~/data",
            train=False,
            download=True,
            transform=transform,
        )

    # Create data loaders
    train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)

    return train_dataloader, test_dataloader


# Model Definition
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28 * 28, 512),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(512, 10),
            nn.ReLU(),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


def train_func_per_worker(config: Dict):
    lr = config["lr"]
    epochs = config["epochs"]
    batch_size = config["batch_size_per_worker"]

    # Get dataloaders inside the worker training function
    train_dataloader, test_dataloader = get_dataloaders(batch_size=batch_size)

    # [1] Prepare Dataloader for distributed training
    # Shard the datasets among workers and move batches to the correct device
    # =======================================================================
    train_dataloader = ray.train.torch.prepare_data_loader(train_dataloader)
    test_dataloader = ray.train.torch.prepare_data_loader(test_dataloader)

    model = NeuralNetwork()

    # [2] Prepare and wrap your model with DistributedDataParallel
    # Move the model to the correct GPU/CPU device
    # ============================================================
    model = ray.train.torch.prepare_model(model)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)

    # Model training loop
    for epoch in range(epochs):
        if ray.train.get_context().get_world_size() > 1:
            # Required for the distributed sampler to shuffle properly across epochs.
            train_dataloader.sampler.set_epoch(epoch)

        model.train()
        for X, y in tqdm(train_dataloader, desc=f"Train Epoch {epoch}"):
            pred = model(X)
            loss = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        model.eval()
        test_loss, num_correct, num_total = 0, 0, 0
        with torch.no_grad():
            for X, y in tqdm(test_dataloader, desc=f"Test Epoch {epoch}"):
                pred = model(X)
                loss = loss_fn(pred, y)

                test_loss += loss.item()
                num_total += y.shape[0]
                num_correct += (pred.argmax(1) == y).sum().item()

        test_loss /= len(test_dataloader)
        accuracy = num_correct / num_total

        # [3] Report metrics to Ray Train
        # ===============================
        ray.train.report(metrics={"loss": test_loss, "accuracy": accuracy})


def train_fashion_mnist(num_workers, cpus_per_worker, use_gpu, gpus_per_worker):
    global_batch_size = 32

    train_config = {
        "lr": 1e-3,
        "epochs": 10,
        "batch_size_per_worker": global_batch_size // num_workers,
    }

    # Configure computation resources
    scaling_config = ScalingConfig(
        num_workers=num_workers,
        use_gpu=use_gpu,
        resources_per_worker={"GPU": gpus_per_worker, "CPU": cpus_per_worker}
    )

    # Initialize a Ray TorchTrainer
    trainer = TorchTrainer(
        train_loop_per_worker=train_func_per_worker,
        train_loop_config=train_config,
        scaling_config=scaling_config,
    )

    # [4] Start distributed training
    # Run `train_func_per_worker` on all workers
    # =============================================
    result = trainer.fit()
    print(f"Training result: {result}")


if __name__ == "__main__":
    num_workers = int(os.getenv("NUM_WORKERS", "1"))
    cpus_per_worker = int(os.getenv("CPUS_PER_WORKER", "100"))
    gpus_per_worker = int(os.getenv("GPUS_PER_WORKER", "1"))
    train_fashion_mnist(num_workers=num_workers, cpus_per_worker=cpus_per_worker,use_gpu=True,gpus_per_worker=gpus_per_worker)

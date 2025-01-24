import math
from collections import OrderedDict
from typing import List, Optional, Tuple, Dict
from nidum.helpers import pretty_print_bytes, pretty_print_bytes_per_second
from nidum.topology.topology import Topology
from nidum.topology.partitioning_strategy import Partition
from nidum.download.hf.hf_helpers import RepoProgressEvent
from nidum.topology.device_capabilities import UNKNOWN_DEVICE_CAPABILITIES
from rich.console import Console, Group
from rich.text import Text
from rich.live import Live
from rich.style import Style
from rich.table import Table
from rich.layout import Layout
from rich.syntax import Syntax
from rich.panel import Panel
from rich.markdown import Markdown


class TopologyViz:
    def __init__(self, chatgpt_api_endpoints: List[str] = [], web_chat_urls: List[str] = []):
        self.chatgpt_api_endpoints = chatgpt_api_endpoints
        self.web_chat_urls = web_chat_urls
        self.topology = Topology()
        self.partitions: List[Partition] = []
        self.node_id = None
        self.node_download_progress: Dict[str, RepoProgressEvent] = {}

    def log_topology(self):
        """Logs the current state of the topology to the terminal."""
        node_count = len(self.topology.nodes)
        print(f"Nidum Cluster Status: {node_count} node{'s' if node_count != 1 else ''}")
        for i, partition in enumerate(self.partitions):
            device_capabilities = self.topology.nodes.get(partition.node_id, UNKNOWN_DEVICE_CAPABILITIES)
            print(f"  Node {i + 1}:")
            print(f"    - Model: {device_capabilities.model}")
            print(f"    - Memory: {device_capabilities.memory // 1024}GB")
            print(f"    - TFLOPS: {device_capabilities.flops.fp16}")
            print(f"    - Partition: [{partition.start:.2f}-{partition.end:.2f}]")

    def log_download_progress(self):
        """Logs the download progress of nodes."""
        print("Download Progress:")
        for node_id, progress in self.node_download_progress.items():
            print(f"  Node ID: {node_id}")
            print(f"    - Repo: {progress.repo_id}@{progress.repo_revision}")
            print(f"    - Completed Files: {progress.completed_files}/{progress.total_files}")
            print(f"    - Speed: {pretty_print_bytes_per_second(progress.overall_speed)}")
            print(f"    - ETA: {progress.overall_eta}")
            print(f"    - Total Downloaded: {pretty_print_bytes(progress.downloaded_bytes)} / {pretty_print_bytes(progress.total_bytes)}")

    def update_visualization(self, topology: Topology, partitions: List[Partition], node_id: Optional[str] = None, node_download_progress: Dict[str, RepoProgressEvent] = {}):
        self.topology = topology
        self.partitions = partitions
        self.node_id = node_id
        if node_download_progress:
            self.node_download_progress = node_download_progress
        self.refresh_logs()

    def refresh_logs(self):
        """Refresh logs by updating the terminal output in place."""
        # Clear the terminal
        # print("\033[H\033[J", end="")  # Move to top-left and clear the screen

        # Update topology status
        if self.topology.nodes:
            self.log_topology()
        else:
            print("Nidum Cluster Status: No nodes detected.\n")

        # Update download progress
        if self.node_download_progress:
            self.log_download_progress()
        else:
            print("No downloads in progress.\n")

    def final_response(self):
        """Display the final response once everything is complete."""
        self.log_topology()
        self.log_download_progress()
    def update_prompt_output(self, request_id: str, output: Optional[str] = None):
        """Dummy method to avoid crashes when called."""
        pass
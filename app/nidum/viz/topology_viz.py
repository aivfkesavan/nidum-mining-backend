import logging
import os
import math
from collections import OrderedDict
from typing import List, Optional, Dict
from nidum.helpers import pretty_print_bytes, pretty_print_bytes_per_second
from nidum.topology.topology import Topology
from nidum.topology.partitioning_strategy import Partition
from nidum.download.hf.hf_helpers import RepoProgressEvent
from nidum.topology.device_capabilities import UNKNOWN_DEVICE_CAPABILITIES

# Set up logging
log_file = os.path.join(os.getcwd(), "nidum_topology.log")
logging.basicConfig(
    filename=log_file,
    filemode="w",  # Overwrites file on each run; change to "a" to append logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TopologyViz:
    def __init__(self, chatgpt_api_endpoints: List[str] = [], web_chat_urls: List[str] = []):
        self.chatgpt_api_endpoints = chatgpt_api_endpoints
        self.web_chat_urls = web_chat_urls
        self.topology = Topology()
        self.partitions: List[Partition] = []
        self.node_id = None
        self.node_download_progress: Dict[str, RepoProgressEvent] = {}

    def log_topology(self):
        """Logs the current state of the topology."""
        node_count = len(self.topology.nodes)
        logger.info(f"Nidum Cluster Status: {node_count} node{'s' if node_count != 1 else ''}")
        
        for i, partition in enumerate(self.partitions):
            device_capabilities = self.topology.nodes.get(partition.node_id, UNKNOWN_DEVICE_CAPABILITIES)
            logger.info(f"  Node {i + 1}:")
            logger.info(f"    - Model: {device_capabilities.model}")
            logger.info(f"    - Memory: {device_capabilities.memory // 1024}GB")
            logger.info(f"    - TFLOPS: {device_capabilities.flops.fp16}")
            logger.info(f"    - Partition: [{partition.start:.2f}-{partition.end:.2f}]")

    def log_download_progress(self):
        """Logs the download progress of nodes."""
        logger.info("Download Progress:")
        for node_id, progress in self.node_download_progress.items():
            logger.info(f"  Node ID: {node_id}")
            logger.info(f"    - Repo: {progress.repo_id}@{progress.repo_revision}")
            logger.info(f"    - Completed Files: {progress.completed_files}/{progress.total_files}")
            logger.info(f"    - Speed: {pretty_print_bytes_per_second(progress.overall_speed)}")
            logger.info(f"    - ETA: {progress.overall_eta}")
            logger.info(f"    - Total Downloaded: {pretty_print_bytes(progress.downloaded_bytes)} / {pretty_print_bytes(progress.total_bytes)}")

    def update_visualization(self, topology: Topology, partitions: List[Partition], node_id: Optional[str] = None, node_download_progress: Dict[str, RepoProgressEvent] = {}):
        self.topology = topology
        self.partitions = partitions
        self.node_id = node_id
        if node_download_progress:
            self.node_download_progress = node_download_progress
        self.refresh_logs()

    def refresh_logs(self):
        """Refresh logs by updating the log file instead of terminal output."""
        if self.topology.nodes:
            self.log_topology()
        else:
            logger.info("Nidum Cluster Status: No nodes detected.\n")

        if self.node_download_progress:
            self.log_download_progress()
        else:
            logger.info("No downloads in progress.\n")

    def final_response(self):
        """Display the final response once everything is complete."""
        self.log_topology()
        self.log_download_progress()

    def update_prompt_output(self, request_id: str, output: Optional[str] = None):
        """Dummy method to avoid crashes when called."""
        pass

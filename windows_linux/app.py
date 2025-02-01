
# def get_system_info():
#     data={
#     "machineConfig": {
#         "os": "macOS 15.2",
#         "architecture": "arm64",
#         "cpu": "Apple M1 Max",
#         "totalRam": "34.36 GB",
#         "storage": "NaN GB",
#         "bandwidth": "0.00 Mbps",
#         "connectionSpeed": "40 Mbps",
#         "numberOfCores": 10,
#         "ip": "192.168.1.2"
#     }
# }
#     return data

import os
import sys
import json
import requests
import subprocess
import psutil
import platform
import socket
import logging
import re
import signal
import threading
import time
import websocket  # pip install websocket-client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

HOST = "https://apiv3.chain.nidum.ai/api"

# Global Variables
device_id = None
cluster_id = None
netbird_ip = None
peer_id = None
api_token = None
last_message_time = None  # For websocket heartbeat tracking

def get_system_info():
    """Dynamically fetch system details."""
    try:
        # Get storage details
        disk_info = psutil.disk_usage('/')
        total_storage = round(disk_info.total / (1024**3), 2)  # Convert to GB

        # Get IP address
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            ip_address = "Unknown"

        # Get CPU name (Linux systems may not return platform.processor())
        try:
            cpu_info = subprocess.check_output("lscpu | grep 'Model name:'", shell=True, text=True).strip()
            cpu_name = re.sub(r"Model name:\s+", "", cpu_info)
        except Exception:
            cpu_name = platform.processor() or "Unknown"

        # Get bandwidth (as a placeholder)
        bandwidth = 100  # Placeholder value, real measurement requires additional setup

        # Get connection speed (Placeholder, real-world requires network testing)
        connection_speed = 50  # Placeholder

        system_info = {
            "machineConfig": {
                "os": f"{platform.system()} {platform.release()}",
                "architecture": platform.machine(),
                "cpu": cpu_name,
                "totalRam": round(psutil.virtual_memory().total / (1024**3), 2),  # Convert to GB
                "storage": total_storage,
                "bandwidth": bandwidth,
                "connectionSpeed": connection_speed,
                "numberOfCores": psutil.cpu_count(logical=False),
                "ip": ip_address
            }
        }

        logging.info(f"📡 System Info: {system_info}")
        return system_info

    except Exception as e:
        logging.error(f"Error fetching system info: {e}")
        return {"machineConfig": {}}
def fetch_cluster_id():
    """Call API to fetch cluster ID."""
    global cluster_id
    url = f"{HOST}/device/v3/{device_id}/cluster/eligible"
    payload = json.dumps(get_system_info())
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}

    logging.info(f"🔄 Requesting Cluster ID from {url}")
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code != 200:
        logging.error(f"❌ Error fetching cluster ID: {response.text}")
        sys.exit(1)

    response_data = response.json()
    cluster_id = response_data.get("eligibleClusters", [{}])[0].get("_id")
    if not cluster_id:
        logging.error("❌ Cluster ID is missing in the API response.")
        sys.exit(1)

    logging.info(f"✅ Fetched Cluster ID: {cluster_id}")

def fetch_setup_key():
    """Call API to fetch network setup key."""
    url = f"{HOST}/device/v3/{device_id}/network/key?clusterId={cluster_id}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}

    logging.info(f"🔄 Requesting Setup Key from {url}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"❌ Error fetching setup key: {response.text}")
        sys.exit(1)

    response_data = response.json()
    setup_key = response_data.get("setupKey")

    if not setup_key:
        logging.error("❌ Setup Key is missing in the API response.")
        sys.exit(1)

    logging.info(f"✅ Fetched Setup Key: {setup_key}")
    return setup_key

def install_netbird(setup_key):
    """Run NetBird and extract NetBird IP."""
    global netbird_ip
    logging.info("🚀 Running NetBird setup on Ubuntu...")

    command = f'''
    export NB_MANAGEMENT_URL="https://network.nidum.ai" && \
    netbird service install && \
    netbird service start && \
    netbird up --setup-key {setup_key}
    '''

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    logging.info("NetBird up output: %s", stdout)

    if process.returncode != 0:
        logging.error("NetBird up error: %s", stderr)
        sys.exit(1)

    logging.info("📡 Checking NetBird status...")
    result = subprocess.run("netbird status", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    status_output = result.stdout
    logging.info("NetBird status output: %s", status_output)

    if result.returncode != 0:
        logging.error("NetBird status error: %s", result.stderr)
        sys.exit(1)

    # Extract NetBird IP
    match = re.search(r"NetBird IP: (\d+\.\d+\.\d+\.\d+)", status_output)
    if match:
        netbird_ip = match.group(1)
        logging.info(f"✅ Extracted NetBird IP: {netbird_ip}")
    else:
        logging.error("❌ Failed to extract NetBird IP.")
        sys.exit(1)

def register_peer():
    """Send clusterId and NetBird IP to the API to get peer ID."""
    global peer_id
    url = f"{HOST}/device/v3/{device_id}/peer"
    payload = json.dumps({"clusterId": cluster_id, "netbirdIP": netbird_ip})
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}

    logging.info(f"🔄 Registering Peer with Cluster ID {cluster_id} and NetBird IP {netbird_ip}...")
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code != 200:
        logging.error(f"❌ Error registering peer: {response.text}")
        sys.exit(1)

    response_data = response.json()
    peer_id = response_data.get("peerId")

    if not peer_id:
        logging.error("❌ Peer ID is missing in the API response.")
        sys.exit(1)

    logging.info(f"✅ Registered Peer ID (Machine ID): {peer_id}")

def extract_numeric(value):
    """Extract numeric part from strings like '34.36 GB' or '0.00 Mbps'."""
    match = re.search(r"([\d.]+)", str(value))
    return float(match.group(1)) if match else 0.0

def register_machine():
    """Send machine information to API after registering peer."""
    url = f"{HOST}/device/v3/cluster/{cluster_id}"
    system_info = get_system_info()["machineConfig"]

    payload = {
        "machineInfo": {
            "machineId": peer_id,  # Peer ID becomes machine ID
            "bandwidth": extract_numeric(system_info["bandwidth"]),
            "ram": extract_numeric(system_info["totalRam"]),
            "connectionSpeed": extract_numeric(system_info["connectionSpeed"]),
            "system": system_info["cpu"],
            "ip": netbird_ip,  # Now passing NetBird IP instead of local IP
            "appId": device_id  # Device ID becomes App ID
        }
    }

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}

    logging.info(f"🔄 Registering Machine {peer_id} in Cluster {cluster_id} with NetBird IP: {netbird_ip}...")
    
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        logging.error(f"❌ Error registering machine: {response.text}")
        sys.exit(1)

    logging.info(f"✅ Successfully registered machine {peer_id} in cluster {cluster_id}.")

def delete_peer():
    """Call API to delete peer when container stops."""
    if not device_id or not cluster_id or not netbird_ip:
        logging.warning("⚠️ Missing parameters, skipping peer deletion.")
        return

    url = f"{HOST}/device/v3/{device_id}/peer"
    payload = json.dumps({"clusterId": cluster_id, "netbirdIP": netbird_ip})
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"}

    logging.info(f"🛑 Deleting peer {netbird_ip} from Cluster {cluster_id} before exit...")
    response = requests.delete(url, data=payload, headers=headers)

    if response.status_code == 200:
        logging.info(f"✅ Successfully deleted peer {netbird_ip} from cluster {cluster_id}.")
    else:
        logging.error(f"❌ Error deleting peer: {response.text}")

def handle_shutdown(signum, frame):
    logging.info("⚠️ Received stop signal, cleaning up...")
    delete_peer()
    logging.info("🛑 Exiting container.")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

def run_websocket():
    """
    Establish a websocket connection and send a heartbeat message ("10s")
    every 10 seconds. If no message is received for 30 seconds, the container
    is stopped.
    """
    # Build the websocket URL using the device and cluster IDs.
    # Note: Adjust the ws:// scheme to wss:// if TLS is required.
    websocket_url = f"wss://apiv3.chain.nidum.ai/api/v3/{device_id}/watch/{cluster_id}"
    logging.info(f"Connecting to WebSocket URL: {websocket_url}")
    
    global last_message_time
    last_message_time = time.time()
    
    def on_message(ws, message):
        logging.info(f"Received message from websocket: {message}")
        global last_message_time
        last_message_time = time.time()
    
    def on_error(ws, error):
        logging.error(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        logging.info("WebSocket closed")
    
    def on_open(ws):
        logging.info("WebSocket connection opened")
        def run_heartbeat():
            while True:
                try:
                    ws.send("10s")
                    logging.info("Sent heartbeat message: 10s")
                except Exception as e:
                    logging.error("Error sending heartbeat: %s", e)
                    break
                # If no message received in the last 30 seconds, stop container.
                if time.time() - last_message_time > 30:
                    logging.error("No message received in 30 seconds. Stopping container.")
                    delete_peer()
                    os._exit(1)
                time.sleep(10)
        heartbeat_thread = threading.Thread(target=run_heartbeat, daemon=True)
        heartbeat_thread.start()
    
    ws_app = websocket.WebSocketApp(
        websocket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws_app.run_forever()

if __name__ == "__main__":
    # Expecting device_id and api_token as command-line arguments.
    device_id, api_token = sys.argv[1:3]
    
    fetch_cluster_id()
    setup_key = fetch_setup_key()
    install_netbird(setup_key)
    register_peer()
    register_machine()
    
    # Once registration is complete, start the WebSocket connection.
    run_websocket()

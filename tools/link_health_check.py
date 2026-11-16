"""Diagnostic script to measure packet loss and latency of MAVLink endpoint."""

import time
import sys
from core.mavlink_bridge import MAVLinkBridge

def check_health(endpoint: str):
    print(f"Diagnosing MAVLink link on {endpoint}...")
    bridge = MAVLinkBridge(endpoint=endpoint)
    if not bridge.connect(timeout=6):
        print("FAILED: No heartbeat detected.")
        sys.exit(1)

    print("Heartbeat verified. Sampling 20 packets...")
    start = time.time()
    samples = 0
    while time.time() - start < 4.0 and samples < 20:
        snap = bridge.get_snapshot()
        if snap.is_link_alive():
            samples += 1
        time.sleep(0.2)

    bridge.disconnect()
    print(f"SUCCESS: Link healthy. Received {samples} samples.")

if __name__ == "__main__":
    ep = sys.argv[1] if len(sys.argv) > 1 else "udp:127.0.0.1:14550"
    check_health(ep)

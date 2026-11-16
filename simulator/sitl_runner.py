"""SITL Process Launcher and Simulator Controller."""

import os
import sys
import time
import subprocess
import logging
from typing import Optional
from simulator.sitl_mock_server import MockSITLServer

logger = logging.getLogger("SITLRunner")


class SITLRunner:
    """Manages starting and stopping either the internal mock SITL or external ArduPilot SITL."""

    def __init__(self, mode: str = "mock", port: int = 14550):
        self.mode = mode.lower()
        self.port = port
        self.mock_server: Optional[MockSITLServer] = None
        self.external_process: Optional[subprocess.Popen] = None

    def start(self):
        if self.mode == "mock":
            logger.info("Starting Built-in Lightweight MAVLink SITL Server...")
            self.mock_server = MockSITLServer(target_port=self.port)
            self.mock_server.start()
        elif self.mode == "ardupilot":
            logger.info("Spawning external ArduPilot SITL (sim_vehicle.py)...")
            cmd = [
                "sim_vehicle.py",
                "-v", "ArduCopter",
                "-f", "quad",
                "--out", f"127.0.0.1:{self.port}"
            ]
            try:
                self.external_process = subprocess.Popen(cmd)
            except FileNotFoundError:
                logger.error("sim_vehicle.py not found in PATH! Falling back to built-in mock SITL.")
                self.mock_server = MockSITLServer(target_port=self.port)
                self.mock_server.start()

    def stop(self):
        if self.mock_server:
            self.mock_server.stop()
            self.mock_server = None
        if self.external_process:
            self.external_process.terminate()
            self.external_process.wait(timeout=2.0)
            self.external_process = None

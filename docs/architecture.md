# System Architecture & Design Philosophy

The KKRTI UAV codebase follows a layered, loosely coupled design:

1. **Protocol Layer (`core/mavlink_bridge.py`)**:
   Runs background I/O threads using non-blocking MAVLink sockets. Protects shared state with thread locks.

2. **Domain Layer (`core/telemetry.py` & `core/drone_controller.py`)**:
   Pure Python dataclasses and high-level async-safe methods (`arm`, `takeoff`, `goto_location`, `return_to_launch`).

3. **Safety Layer (`core/geofence_manager.py` & `core/failsafe_manager.py`)**:
   Evaluates perimeter bounds on every telemetry tick. Emits non-recoverable emergency commands if breached.

4. **Simulation Layer (`simulator/sitl_mock_server.py`)**:
   Emulates flight dynamics and standard ArduPilot autopilot messages to decouple mission coding from heavy simulation stacks.

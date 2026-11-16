"""Hard emergency cutoff mechanism to immediately terminate motor outputs."""

from pymavlink import mavutil

def trigger_emergency_kill(master) -> bool:
    """Sends forceful disarm to cut motor throttle instantly."""
    if not master:
        return False
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,         # Disarm
        21196.0,   # Force override flag
        0, 0, 0, 0, 0
    )
    return True

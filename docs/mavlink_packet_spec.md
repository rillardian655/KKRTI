# MAVLink Protocol Packet Architecture

This document describes the message IDs and streaming rates used by the KKRTI bridge:

| Message Name | Message ID | Frequency | Description |
|---|---|---|---|
| HEARTBEAT | 0 | 1 Hz | Autopilot operational mode and armed flag |
| SYS_STATUS | 1 | 2 Hz | Battery voltage, current draw, remaining capacity |
| GPS_RAW_INT | 24 | 5 Hz | 3D fix type, satellite count, eph/epv |
| ATTITUDE | 30 | 10 Hz | Roll, pitch, yaw angles in radians |
| GLOBAL_POSITION_INT | 33 | 10 Hz | GPS latitude, longitude, and relative altitude |
| HOME_POSITION | 242 | 1 Hz | Geodetic home base reference coordinates |

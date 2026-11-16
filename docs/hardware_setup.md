# Hardware Wiring & Telemetry Setup Guide

## Pixhawk / Cube Pinout Reference

- **TELEM 1**: Connect to SiK 915MHz/433MHz Telemetry Radio (Baud: 57600)
- **TELEM 2**: Connect to Companion Computer (Raspberry Pi / Jetson Nano) via UART (Baud: 921600)
- **SERVO OUT 9**: Connect to payload drop mechanical release servo (PWM: 1000 closed, 2000 release)
- **I2C 1**: Compass & Barometer sensor bus
- **GPS 1**: Primary GPS + Compass module

## Linux USB Serial Permissions

Ensure your Linux user belongs to the `dialout` or `uucp` group:
```bash
sudo usermod -aG uucp $USER
```

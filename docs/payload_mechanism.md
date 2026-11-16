# Payload Drop Servo Release Calibration

## Mechanical Integration

1. Servo connects to AUX channel (SERVO9) on the flight controller.
2. Ensure servo horn does not bind at mechanical limits.

## PWM Trigger Values

- **Locked (Hold)**: PWM 1000 us
- **Released (Drop)**: PWM 2000 us
- **Hold Duration**: 1.5 seconds recommended to ensure physical package release before climb.

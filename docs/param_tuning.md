# Autopilot PID Parameter Tuning Reference

## Rate Controller Tuning Guidelines

1. **Roll/Pitch P Gain**: Increase until slight oscillation occurs, then reduce by 15%.
2. **Roll/Pitch D Gain**: Increases damping to suppress oscillation; keep low to avoid high-frequency motor heating.
3. **Roll/Pitch I Gain**: Eliminates steady-state wind offset; typically set equal to P gain.
4. **Altitude Hold P Gain (`PSC_POSZ_P`)**: Governs vertical climb responsiveness.

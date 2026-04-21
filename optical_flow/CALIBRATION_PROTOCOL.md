# Optical Flow Calibration Protocol

## Purpose

Convert raw optical flow output (`dx`, `dy`, counts/sample) into physical surface speed (m/s) with a repeatable method that transfers into a ROS2 C++ node.

## Recommended Rig

- Spinning disk with known radius `r` (meters)
- Constant RPM setpoints (both directions if possible)
- Sensor mounted at fixed height and angle
- Stable lighting and textured surface
- Keep LED level fixed during each run; tune level between runs only.

Reference tangential speed:

- `v_ref = 2 * pi * r * rpm / 60`

## Data Collection Procedure

1. Warm up sensor for ~30 seconds.
2. Run stream logging at fixed poll target:
   - `python src/of_diagnostics.py --mode stream-log --stream-seconds 30 --stream-target-hz 30 --stream-led-on --stream-led-percent 100 --log-dir logs`
3. For each RPM setpoint/direction:
   - Hold steady for 20-30 seconds
   - Record run metadata: `rpm`, `radius_m`, direction, surface type, height
4. Repeat across at least 5 speed levels and both directions.

## Fit Scale Factor

For each run:

- Compute robust mean of `speed_counts_s` (trim out obvious outliers if needed).
- Compute `v_ref` from known `rpm` and `r`.
- Scale estimate: `k_i = v_ref / speed_counts_s_mean` (m per count).

Final scale:

- `k = median(k_i)` over all valid runs.

Then physical speed estimate becomes:

- `v_est_mps = k * speed_counts_s`

## Validation

- Apply `k` on held-out runs.
- Report mean absolute percentage error (MAPE).
- Target error depends on application; for closed-loop control, also validate transient response and directional sign consistency.

## Notes For ROS2 C++ Integration

- Use Python diagnostics only for characterization and calibration.
- Production data path should be implemented in C++ for lower jitter and tighter loop timing.
- Store `k` and quality thresholds in ROS2 param YAML.

## Rotation / Angular Motion

A single flow sensor does not directly provide yaw rate.

For rotation-aware control, fuse with:

- IMU gyro (recommended), or
- multiple flow sensors with known spacing.

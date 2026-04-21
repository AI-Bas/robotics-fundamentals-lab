# Optical Flow (PAA5100JE)

Raspberry Pi optical-flow experiment project using the `pmw3901` Python library and SPI.

## Hardware Context

- Sensor: PAA5100JE breakout
- Interface: SPI
- Expected use range: close surface tracking (roughly 15-35mm)

The board has two white SMD illumination LEDs near the lens. Community reports and vendor notes indicate they are illumination LEDs controlled by sensor registers (not standalone GPIO LEDs).

## What Is Known About LED Control

- Some users have successfully toggled LED behavior by writing register `0x6F` after selecting register bank via `0x7F`.
- Common values observed in community examples:
  - off: `0x00`
  - medium/on test value: `0x1C`
  - max (from other driver constants): `0xD5`
- Python support varies by library version:
  - some installs expose a high-level `set_led(...)`
  - otherwise a lower-level/private register write path is needed

Because this is partly undocumented behavior, treat LED tests as experimental and non-portable.

## Setup

`pmw3901` 1.x depends on **`gpiod`** and **`gpiodevice`** (Pimoroni GPIO helper). If `gpiod` fails to build, install headers first:

```bash
sudo apt update
sudo apt install -y libgpiod-dev python3-dev
```

Then create the venv and install:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Experimental Script

`src/of_experimental.py` is kept as an experimental wrapper.
Core functionality now lives in dedicated scripts by use case.

Hardware and SPI defaults are read from:

- `config/sensor_config.yaml`

Edit that file first, then run tests. CLI flags still override config values when provided.

Run:

```bash
source .venv/bin/activate
python src/of_experimental.py --help
python src/of_experimental.py --mode info
```

Recommended sequence (delegated wrappers):

1. `python src/of_experimental.py --mode info`
2. `python src/of_experimental.py --mode motion --seconds 15`
3. `python src/of_experimental.py --mode led --led-mode blink --blink-count 6 --led-percent 30`

If needed, override YAML values temporarily:

- `python src/of_experimental.py --mode led --spi-cs 0`

Additional advanced experiments (when available in your local `pmw3901` build):

- `python src/of_experimental.py --mode probe`
- `python src/of_experimental.py --mode burst --samples 20 --sample-period 0.03`
- `python src/of_experimental.py --mode frame --samples 5`
- `python src/of_experimental.py --mode register-read --register 0x07`

Why this matters: these modes let you probe capabilities and sample raw-ish data paths before committing to ROS2 runtime features.

If LED control is not exposed in your local package version, use communication and stream modes for validation.

## Dedicated Diagnostics Script

Use `src/of_diagnostics.py` for repeatable hardware troubleshooting and quick benchmarking.

Examples:

```bash
source .venv/bin/activate

# Bus/wiring presence only
python src/of_diagnostics.py --mode preflight

# Communication samples
python src/of_diagnostics.py --mode comm --comm-samples 20

# LED sanity blink (default level is max brightness if omitted)
python src/of_diagnostics.py --mode led --led-mode blink --blink-count 8 --blink-period 0.35
python src/of_diagnostics.py --mode led --led-mode constant --blink-period 1.0 --led-percent 30
python src/of_diagnostics.py --mode led --led-mode breathe --breathe-up-s 1.0 --breathe-down-s 1.0

# Max poll-rate benchmark
python src/of_diagnostics.py --mode benchmark --bench-seconds 10

# Max poll-rate benchmark + CSV telemetry
python src/of_diagnostics.py --mode benchmark-log --bench-seconds 10 --log-dir logs

# Stable-rate sweep to estimate highest sustainable polling rate
python src/of_diagnostics.py --mode rate-sweep --sweep-start-hz 10 --sweep-stop-hz 140 --sweep-step-hz 10 --sweep-hold-s 2

# Future feature (ROS2 integration phase): dedicated hb-tune mode with runtime recommendation output
# planned: python src/of_diagnostics.py --mode hb-tune ...

# Communication samples + CSV telemetry
python src/of_diagnostics.py --mode comm-log --comm-samples 50 --log-dir logs

# Optional memory column (off by default to keep logging lean)
python src/of_diagnostics.py --mode benchmark-log --bench-seconds 10 --log-dir logs --include-mem

# Continuous operation stream with reliability flags
python src/of_diagnostics.py --mode stream-log --stream-seconds 60 --stream-target-hz 30 --log-dir logs

# Stream with LED forced on for low-light testing/calibration tuning
python src/of_diagnostics.py --mode stream-log --stream-seconds 60 --stream-target-hz 30 --stream-led-on --stream-led-percent 100 --log-dir logs

# Run all checks in sequence
python src/of_diagnostics.py --mode all
```

CSV logs include timing/error fields, monotonic/process clock stamps, motion deltas, scalar flow speed, and flow heading.
Each logging mode also writes a JSON summary that is easier to consume from ROS2 launch/config scripts.

## Interpreting Motion Values

- `dx`, `dy` are optical-flow counts per sample, not meters.
- `speed_counts` is `sqrt(dx^2 + dy^2)` in counts/sample.
- `speed_counts_s` is counts/second using measured `dt_s`.
- `flow_heading_deg` is the 2D flow vector direction from `atan2(dy, dx)`.
- To convert counts to physical velocity (m/s), you will need calibration at known height/surface/lighting.

### About Rotation

This single optical flow sensor does not directly report yaw/rotation rate. You can estimate robot rotation by sensor fusion (IMU gyro + flow) or by using multiple spatially-separated flow sensors.

## ROS2 Preparation

- Export measured diagnostics into ROS2 parameter YAML:

```bash
python src/of_export_ros2_profile.py --log-dir logs --output config/ros2_optical_flow_profile.yaml --node-name optical_flow_node
```

- Result file is designed for ROS2 node parameters (`ros__parameters`) and includes:
  - recommended `poll_hz`
  - quality thresholds for unreliable data gating
  - calibration placeholder (`counts_to_mps_scale`)
  - source summary files used to generate the profile

> Python scripts here are for experimentation and calibration.  
> For final real-time ROS2 control loops, implement the runtime node in C++.

## Smoke Test Meaning

A "sensor smoke test" is a fast basic health check to catch obvious faults before deep testing:

- SPI device node exists
- sensor initializes
- at least one valid motion read returns
- no immediate exceptions

It does **not** prove accuracy or calibration; it only confirms the sensor path is alive.

## Calibration

Use the spinning-disk/known-velocity procedure in `CALIBRATION_PROTOCOL.md` to convert counts to m/s for real surface speed estimation.

## Script Roles (ROS2 Prep)

To keep use-cases separated while developing in Python:

- `src/of_sensor.py` - shared sensor interaction and LED control primitives
- `src/of_sensor_smoke.py` - fast health/smoke verification
- `src/of_experimental.py` - experimental wrapper with delegated and raw-access experiments
- `src/of_diagnostics.py` - deep troubleshooting, streaming, benchmark, sweep
- `src/of_log_motion.py` - continuous stream logging wrapper
- `src/of_log_tests.py` - benchmark/sweep wrapper
- `src/of_calibration.py` - brightness/scale calibration for profile updates
- `src/of_graph.py` - graph diagnostics/calibration trends and optimization results
- `src/of_export_ros2_profile.py` - diagnostics -> ROS2 parameter YAML
- `src/of_main.py` - simple top-level task router

Examples:

```bash
# smoke test
python src/of_sensor_smoke.py --samples 10
python src/of_sensor_smoke.py --samples 10 --led-up-s 1.0 --led-down-s 1.0
python src/of_sensor_smoke.py --samples 10 --led-final-percent 10

# continuous stream logging
python src/of_log_motion.py --seconds 60 --target-hz 30 --log-dir logs
python src/of_log_motion.py --seconds 60 --target-hz 30 --stream-led-on --stream-led-percent 100 --log-dir logs

# benchmark + rate sweep
python src/of_log_tests.py --mode both --bench-seconds 20 --log-dir logs

# calibration (stationary + known velocity reference)
python src/of_calibration.py --target-hz 20 --window-s 3 --reference-velocity-mps 0.5 --log-dir logs

# graphs and optimization trends
python src/of_graph.py --log-dir logs --out-dir logs/plots

# task router variant
python src/of_main.py smoke --samples 10
python src/of_main.py stream-log --seconds 60 --target-hz 30
python src/of_main.py graph --log-dir logs --out-dir logs/plots
```

## Logging Notes
Key CSV/JSON outputs are produced by diagnostics and wrappers in `logs/`.
For tracked references, see `optical_flow/log_examples/`.

## Minimal Unit Tests (Development Practice)

Unit tests here focus on pure logic and mocked sensor behavior, not hardware timing:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

Included starter tests in `tests/test_of_sensor_unit.py` show how to validate:

- LED percent mapping bounds
- sensor capability probing output
- motion burst snapshot parsing with mocked register reads

Production guidance:
- Keep hardware-on-Pi checks in diagnostics/smoke scripts (integration tests).
- Keep fast deterministic logic checks in `pytest` unit tests.

LED brightness interface guidance:
- Use `--led-*-percent` in the human-friendly `0-100` range for CLI and config.
- Internally map that to sensor register levels for hardware writes.
- Allow float input for tuning, while effectively supporting integer workflows.

## Troubleshooting

- **`Invalid Product ID ... 0x00/0x00`**: SPI is not reading the chip (wrong CE line, bad wiring, SPI disabled, or no power). Check `ls /dev/spidev0.*`, then try `--spi-cs 0` and `--spi-cs 1`. The test script tries both CE lines by default unless you pass `--no-auto-cs`.
- Confirm SPI enabled in `raspi-config`.
- Verify sensor wiring and CS pin choice.
- Keep sensor at suitable height over textured surfaces.
- If values are mostly zero:
  - check illumination/surface texture
  - check rotation and orientation
  - verify library class is `PAA5100`


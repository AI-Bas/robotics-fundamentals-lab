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

## First Test Script (Experimental Wrapper)

`src/paa5100_first_test.py` is kept as an experimental reference wrapper only.
Core functionality now lives in dedicated scripts by use case.

Hardware and SPI defaults are read from:

- `config/sensor_config.yaml`

Edit that file first, then run tests. CLI flags still override config values when provided.

Run:

```bash
source .venv/bin/activate
python src/paa5100_first_test.py --help
python src/paa5100_first_test.py --mode info
```

Recommended sequence (delegated wrappers):

1. `python src/paa5100_first_test.py --mode info`
2. `python src/paa5100_first_test.py --mode motion --seconds 15`
3. `python src/paa5100_first_test.py --mode led --blink-count 6 --led-level 28`

If needed, override YAML values temporarily:

- `python src/paa5100_first_test.py --mode led --spi-cs 0`

If LED control is not exposed in your local package version, use communication and stream modes for validation.

## Dedicated Diagnostics Script

Use `src/paa5100_diagnostics.py` for repeatable hardware troubleshooting and quick benchmarking.

Examples:

```bash
source .venv/bin/activate

# Bus/wiring presence only
python src/paa5100_diagnostics.py --mode preflight

# Communication samples
python src/paa5100_diagnostics.py --mode comm --comm-samples 20

# LED sanity blink (default level is max brightness if omitted)
python src/paa5100_diagnostics.py --mode led --blink-count 8 --blink-period 0.35
python src/paa5100_diagnostics.py --mode led --blink-count 8 --blink-period 0.35 --led-level 28

# Max poll-rate benchmark
python src/paa5100_diagnostics.py --mode benchmark --bench-seconds 10

# Max poll-rate benchmark + CSV telemetry
python src/paa5100_diagnostics.py --mode benchmark-log --bench-seconds 10 --log-dir logs

# Stable-rate sweep to estimate highest sustainable polling rate
python src/paa5100_diagnostics.py --mode rate-sweep --sweep-start-hz 10 --sweep-stop-hz 140 --sweep-step-hz 10 --sweep-hold-s 2

# Communication samples + CSV telemetry
python src/paa5100_diagnostics.py --mode comm-log --comm-samples 50 --log-dir logs

# Optional memory column (off by default to keep logging lean)
python src/paa5100_diagnostics.py --mode benchmark-log --bench-seconds 10 --log-dir logs --include-mem

# Continuous operation stream with reliability flags
python src/paa5100_diagnostics.py --mode stream-log --stream-seconds 60 --stream-target-hz 30 --log-dir logs

# Stream with LED forced on for low-light testing/calibration tuning
python src/paa5100_diagnostics.py --mode stream-log --stream-seconds 60 --stream-target-hz 30 --stream-led-on --stream-led-level 213 --log-dir logs

# Run all checks in sequence
python src/paa5100_diagnostics.py --mode all
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
python src/export_ros2_profile.py --log-dir logs --output config/ros2_optical_flow_profile.yaml --node-name optical_flow_node
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

- `src/sensor_smoke.py` - fast health/smoke verification
- `src/paa5100_first_test.py` - experimental reference wrapper (delegates by mode)
- `src/paa5100_diagnostics.py` - deep troubleshooting, streaming, benchmark, sweep
- `src/log_motion.py` - continuous stream logging wrapper
- `src/log_tests.py` - benchmark/sweep wrapper
- `src/export_ros2_profile.py` - diagnostics -> ROS2 parameter YAML
- `src/main.py` - simple top-level task router

Examples:

```bash
# smoke test
python src/sensor_smoke.py --samples 10
python src/sensor_smoke.py --samples 10 --led-level 213 --led-period 0.35

# continuous stream logging
python src/log_motion.py --seconds 60 --target-hz 30 --log-dir logs
python src/log_motion.py --seconds 60 --target-hz 30 --stream-led-on --stream-led-level 213 --log-dir logs

# benchmark + rate sweep
python src/log_tests.py --mode both --bench-seconds 20 --log-dir logs

# task router variant
python src/main.py smoke --samples 10
python src/main.py stream-log --seconds 60 --target-hz 30
```

## Logging Notes
Key CSV/JSON outputs are produced by diagnostics and wrappers in `logs/`.
For tracked references, see `optical_flow/log_examples/`.

## Troubleshooting

- **`Invalid Product ID ... 0x00/0x00`**: SPI is not reading the chip (wrong CE line, bad wiring, SPI disabled, or no power). Check `ls /dev/spidev0.*`, then try `--spi-cs 0` and `--spi-cs 1`. The test script tries both CE lines by default unless you pass `--no-auto-cs`.
- Confirm SPI enabled in `raspi-config`.
- Verify sensor wiring and CS pin choice.
- Keep sensor at suitable height over textured surfaces.
- If values are mostly zero:
  - check illumination/surface texture
  - check rotation and orientation
  - verify library class is `PAA5100`


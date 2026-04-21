# Motion Control Platform Architecture

## 1. Purpose

This architecture is for a modular motion-control platform built around a **Raspberry Pi 4 (8 GB)** running **ROS 2** as the system integrator, with:

- **Raspberry Pi 4** as the main compute and control host
- **RoboClaw 2x15A** motor drivers for brushed DC motor actuation
- **RP2040 / Maker Pi** as an auxiliary modular I/O coprocessor
- **Touchscreen HMI** connected locally to the Pi (HDMI for video, USB for touch)
- **Remote browser access** for monitoring and control
- **CSI camera + NPU HAT** for machine vision
- **I2C sensors** for current / voltage / power monitoring
- **optical flow sensor** over SPI or I2C

The design goal is:

1. Keep the **fastest and most timing-sensitive loops on the Pi**
2. Keep the **Maker Pi non-critical** and modular
3. Use **ROS 2** to integrate sensing, control, diagnostics, HMI, and logging
4. Provide a **local kiosk-style HMI** and an optional **remote browser UI**
5. Avoid unnecessary Linux desktop overhead during normal operation

---

## 2. Top-Level System Split

### Raspberry Pi 4 responsibilities

The Pi should own all core functionality:

- motion-control application logic
- ROS 2 graph and message routing
- motor-driver communication
- high-bandwidth sensors
- camera pipeline
- AI/NPU pipeline
- local and remote HMI backend
- data logging, diagnostics, and fault handling

### Maker Pi / RP2040 responsibilities

The Maker Pi should stay auxiliary and modular:

- buttons
- rotary encoder / jog wheel
- tiny OLED status page
- quick experimental sensors
- small local status indicators
- optional ToF / ultrasonic / utility I/O

**Do not make the Maker Pi part of the critical control path.**
If it disconnects, the robot should still keep safe state handling, diagnostics, and core actuation on the Pi.

---

## 3. Recommended Compute and Software Stack

## Base OS

Recommended:

- **Raspberry Pi OS Lite 64-bit**

Reason:

- lighter than a full desktop install
- easier to keep deterministic enough for robotics work on Pi hardware
- still supports adding only the graphical pieces you actually need

### Runtime model

Use one OS image with two operating styles:

- **Normal operation**: control services + local HMI kiosk
- **Maintenance / troubleshooting**: optional desktop session or remote shell access

This is better than trying to maintain separate “desktop” and “server” installs.

---

## 4. ROS 2 Node Architecture

Use ROS 2 as the integration layer, but do **not** put every hard timing requirement through slow, generic message paths if a tighter local loop is needed.

### Recommended ROS 2 subsystems

#### A. `roboclaw_driver_node` (C++)
Handles:

- Packet Serial communication to RoboClaw
- readback of encoder counts, motor speed, current, voltage, status, faults
- command output for velocity / position / duty / current-limited motion as supported
- watchdog and comms timeout handling

Publishes example topics:

- `/drive/left/state`
- `/drive/right/state`
- `/drive/driver_status`
- `/drive/faults`

Subscribes to:

- `/drive/cmd_vel`
- `/drive/cmd_position`
- `/drive/enable`
- `/drive/reset_faults`

#### B. `motion_supervisor_node` (C++)
Handles:

- arbitration between HMI commands, autonomous commands, and test commands
- state machine: disabled / standby / enabled / fault / homing / jog / auto
- safety gating and limits
- command rate limiting, jerk limits, and soft limits
- watchdog behavior if command source disappears

#### C. `sensor_i2c_node`
Handles:

- current / voltage / power monitors
- temperature / auxiliary I2C sensors
- health checks for the I2C bus

#### D. `optical_flow_node`
Use **SPI if available and useful**, otherwise I2C.

Reason:

- SPI is generally the better choice when you want higher update rate and lower bus contention
- reserving I2C for slower housekeeping sensors is sensible

#### E. `camera_node` / `vision_pipeline_node`
Handles:

- CSI camera capture
- preprocessing
- optional AI inference through the NPU stack
- output to ROS 2 topics for detections, image stream, overlays, and health

#### F. `makerpi_bridge_node`
Handles:

- USB serial connection to the RP2040
- parsing modular I/O messages
- publishing button / encoder / OLED / ToF states into ROS 2
- sending status text and small UI state updates back to the RP2040

#### G. `hmi_backend_node`
Handles:

- web API or websocket interface to the local/remote HMI
- conversion between UI actions and ROS 2 service/topic calls
- pushing live status to the browser UI

#### H. `diagnostics_node`
Handles:

- heartbeat aggregation
- node health
- bus health
- NPU / camera / sensor status
- alarm summary
- log tagging

#### I. `recorder_node` / rosbag policy
Handles:

- selective logging during normal operation
- full rosbag capture during troubleshooting or test runs

---

## 5. Control-Loop Placement

### What should stay on the Pi

The Pi should own:

- motion command generation
- supervisory control
- sensor fusion
- high-rate state estimation
- driver feedback polling
- HMI integration

### What should not live on the Maker Pi

Do **not** offload these to the RP2040 unless you later have a very specific reason:

- primary motion loop
- safety-critical state logic
- motor command arbitration
- anything that would break the robot if the USB cable disconnects

### Loop structure recommendation

A practical split is:

- **fast inner loop**: local C++ process / ROS 2 node on Pi
- **mid-rate supervisory loop**: ROS 2 node on Pi
- **slow monitoring / HMI loop**: ROS 2 + web UI

If you need the best dynamic behavior, write the RoboClaw-facing node in **C++**, not Python.

---

## 6. Motor Driver Communication Recommendation

## Correct protocol choice for RoboClaw 2x15A

The corrected driver is the **BasicMicro RoboClaw 2x15A**.
It supports:

- **USB CDC virtual COM port**
- **Packet Serial** on **S1/S2**
- **Simple Serial**
- other modes not relevant here

### What to use

**Recommended for actual control:**

- **Packet Serial over native serial lines**

**Recommended for setup/configuration only:**

- **USB**

### Why

Packet Serial is the right operational protocol because:

- it supports bidirectional communication
- it supports encoder/status feedback
- it supports addressing for multiple RoboClaws
- it is the mode intended for microcontroller/SBC control

Simple Serial is the wrong choice here because it is one-way and does not support encoder feedback the way you want for a closed-loop supervisory system.

### Important correction about RS-485

RoboClaw does **not natively speak RS-485**.
Its documented serial control is **TTL-level packet serial** on S1/S2.

So the right statement is:

- use **RoboClaw Packet Serial** as the protocol
- if you later need longer cable runs or much better noise immunity, add **external differential transceivers / isolation hardware** around that serial link
- but the application-layer protocol remains **RoboClaw Packet Serial**, not “native RS-485”

### Recommended wiring strategy

#### Preferred for bench / prototype

- Pi ↔ isolated USB-UART adapter ↔ RoboClaw packet serial pins

Benefits:

- keeps Pi safer electrically
- easier debug and replacement
- simpler isolation options
- avoids relying on the Pi’s main UART immediately

#### Preferred for compact embedded system after validation

- Pi UART ↔ level-safe / isolated interface ↔ RoboClaw S1/S2

### Strong recommendation

Use **USB to RoboClaw only for Motion Studio setup, firmware/configuration, and bench diagnostics**.
Do **not** make USB the first-choice production control link in a noisy motor system unless testing proves it is stable enough.

### Multi-driver scaling

If you later add multiple RoboClaws:

- use Packet Serial multi-unit mode
- assign unique packet serial addresses
- keep one clean serial bus design
- keep grounds and power wiring disciplined
- strongly consider isolation if the electrical environment is rough

---

## 7. Pi ↔ Maker Pi Communication Recommendation

## Recommended link

Use:

- **USB CDC serial** between Pi and Maker Pi during development and likely in production too

Why:

- easy development workflow
- simple cable and powering model
- no need to burn extra Pi UARTs
- keeps Pi I2C mostly free for sensors
- fits your “modular extension board” goal

### Protocol recommendation

Use a simple framed text or binary protocol over USB serial.

Example message classes:

From Maker Pi to Pi:

- button pressed/released
- encoder delta
- ToF distance
- local fault
- local heartbeat
- local firmware version

From Pi to Maker Pi:

- OLED line update
- status summary
- mode state
- fault banner
- connection health
- heartbeat

### Recommended behavior

The Maker Pi should:

- boot independently
- start a serial heartbeat immediately
- expose all local I/O states periodically or on change
- recover automatically if the Pi side reconnects

The Pi side should:

- treat Maker Pi as optional
- timeout gracefully if it disappears
- republish Maker Pi state into ROS 2 topics

---

## 8. Maker Pi / RP2040 Development Workflow

### What works well

With MicroPython on RP2040, the normal workflow is:

- connect over **USB serial**
- use **REPL**
- push or edit `.py` files on the device
- run and iterate quickly

That gives you the “live update” style workflow you want during development.

### What does not work the way you described

Do **not** assume the board will behave like a normal always-mounted flash drive during normal MicroPython operation.

For RP2040 boards, the USB mass-storage device behavior is associated with **BOOTSEL / UF2 firmware-loading mode**, not the normal runtime editing workflow.

### Practical recommendation

Use one of these development patterns:

1. **Thonny** saving files directly to the board over USB
2. **mpremote / rshell style workflow** over USB serial
3. a custom deploy script from the Pi or dev PC

That is the cleanest path.

### Recommended Maker Pi software structure

Files:

- `boot.py`
- `main.py`
- `io_manager.py`
- `display_manager.py`
- `serial_protocol.py`
- `sensors.py`
- `config.py`

Behavior:

- `boot.py`: minimal safe startup
- `main.py`: init tasks, serial link, heartbeat
- event-driven updates for buttons/encoder
- periodic updates for ToF / OLED / status
- no blocking code
- clean fallback screen if Pi comms are absent

---

## 9. HMI Architecture

## Local HMI

Your local touchscreen can absolutely be the dedicated operator interface.

Recommended physical connection:

- **micro-HDMI** from Pi to display for video
- **USB** from display to Pi for touch input

## Recommended software architecture

Run the HMI locally on the Pi as a **full-screen kiosk application**, not as a full desktop workflow.

### Best implementation

- local web server on Pi
- browser-based HMI
- Chromium or equivalent in kiosk mode on the local display

This gives you:

- local dedicated control panel
- optional remote browser access from another PC
- one shared UI codebase
- easier logging dashboards and camera display
- easier ROS 2 integration through a backend service

### HMI content recommendations

Main pages:

1. **Overview**
   - state
   - enable status
   - motor status
   - power state
   - heartbeat summary

2. **Manual Control**
   - jog
   - setpoint entry
   - mode selection
   - enable / disable
   - reset faults

3. **Sensors**
   - I2C power monitors
   - optical flow
   - ToF
   - camera status
   - Maker Pi I/O

4. **Vision**
   - live camera view
   - detection overlays
   - NPU status

5. **Diagnostics / Logs**
   - ROS node health
   - warnings / errors
   - serial bus status
   - event timeline

6. **Configuration**
   - tunable parameters
   - calibration actions
   - saved presets

### HMI safety rule

Do not make the browser UI the only stop mechanism.

Use:

- hardware power cut / e-stop path
- software disable in ROS 2
- driver watchdogs and command timeout logic

---

## 10. Remote Access Strategy

You want both:

- local HMI on the Pi touchscreen
- remote access from another computer

That is straightforward.

### Recommended split

#### For development and admin

Use:

- **SSH** from your development machine

#### For remote visualization / ops

Use one or both:

- your own **browser-based HMI**
- **Foxglove Bridge + Foxglove** for ROS-native introspection and plotting

### Practical recommendation

Use:

- **custom browser HMI** for actual operator controls
- **Foxglove** for robotics diagnostics, topic inspection, plots, layout panels, and debugging

That is a better split than trying to force all operator UI into Foxglove.

---

## 11. Camera and NPU Path

## Recommended data path

- CSI camera connected directly to the Pi camera interface
- camera driver/pipeline on Pi
- image preprocessing on Pi
- NPU-accelerated inference where supported by your chosen software stack
- results published into ROS 2 topics
- raw or compressed display stream exposed to the HMI

### Recommendation

Do not force the HMI to consume full raw image bandwidth if you do not need it.

Prefer:

- lower-rate preview stream for the UI
- full-rate processing path for machine vision
- optional recorded stream for debugging

---

## 12. Sensor Bus Recommendations

### I2C bus on Pi

Use for:

- current/voltage/power sensors
- slow environmental or housekeeping sensors

Keep it:

- short
- well-pulled-up
- electrically clean

### Optical flow sensor

Prefer:

- **SPI**, if the sensor supports it and you care about update rate / bus isolation

Fallback:

- I2C if the practical update rate is good enough

### Maker Pi experimental sensors

Put fast-changing but non-critical experiments there only if they are not required for the main control loop.

That includes:

- ToF experiments
- ultrasonic experiments
- local utility I/O

If a sensor becomes important to the main control loop, move it to the Pi side.

---

## 13. Recommended ROS 2 Messaging Layout

Example interfaces:

### Commands

- `/system/enable`
- `/system/mode`
- `/motion/cmd_twist`
- `/motion/cmd_setpoint`
- `/motion/jog`

### Motor feedback

- `/motors/left/state`
- `/motors/right/state`
- `/motors/power`
- `/motors/faults`

### Sensors

- `/sensors/power_monitor`
- `/sensors/optical_flow`
- `/sensors/tof`
- `/camera/image_raw`
- `/vision/detections`

### Auxiliary I/O

- `/makerpi/buttons`
- `/makerpi/encoder`
- `/makerpi/oled_status`
- `/makerpi/health`

### Diagnostics

- `/diagnostics`
- `/system/heartbeat`
- `/system/events`

---

## 14. Recommended Process Priorities

### Highest priority

- RoboClaw comms node
- motion supervisor
- state estimation / control logic

### Medium priority

- critical sensors
- camera pipeline
- Maker Pi bridge

### Lower priority

- browser HMI
- logging UI
- non-critical diagnostics rendering
- maintenance tooling

### Practical note

If you need the best behavior:

- use **C++** for motor/control nodes
- keep Python for tooling, glue, and some HMI/backend work only where acceptable

---

## 15. Fault Handling Strategy

The system should survive loss of non-critical modules.

### If Maker Pi disconnects

- show warning
- disable only its functions
- keep core motion stack alive unless those inputs are currently required by the selected mode

### If HMI crashes

- core control continues
- remote SSH still available
- watchdog may drop to safe state if operator command stream is required and disappears

### If RoboClaw comms fail

- immediate fault state
- command output stopped
- supervisor disables motion
- operator alerted locally and remotely

### If camera/NPU fails

- motion stack can remain active if vision is non-essential
- degrade gracefully
- publish degraded mode

---

## 16. Electrical and Noise Recommendations

This matters a lot with motor drivers.

### Strong recommendations

- keep motor power wiring physically separated from logic and data wiring
- use a proper main disconnect and e-stop path
- use short battery and motor leads where possible
- avoid casual USB-ground messes around motor power
- add isolation where needed instead of debugging ghost faults forever

### Specific note for RoboClaw

RoboClaw documentation explicitly warns about:

- regenerative energy issues
- grounding concerns
- USB noise susceptibility in motor environments

So treat USB as a convenience path, not automatically the best production control bus.

---

## 17. Recommended Final Protocol Choices

### Motor drivers

**Recommended:**

- **RoboClaw Packet Serial**
- physical layer: **UART-based**, ideally isolated if needed

**Not recommended as first choice for production control:**

- USB as the main actuator command path

### Maker Pi

**Recommended:**

- **USB CDC serial** with MicroPython

**Fallback:**

- UART if you later want a simpler dedicated electrical interface

### Sensors

- **I2C** for slow housekeeping sensors
- **SPI** for optical flow if possible
- **CSI** for camera

### HMI

- local browser in kiosk mode on Pi touchscreen
- remote browser access to the same web backend
- Foxglove Bridge for ROS-native remote diagnostics

---

## 18. Concrete Recommended Final Architecture

```text
[ Touchscreen Display ]
   ├─ HDMI  <- video from Pi
   └─ USB   <- touch input to Pi

[ Dev Laptop ]
   ├─ SSH -> Pi
   ├─ Browser -> Pi HMI
   └─ Foxglove -> Pi Foxglove Bridge

[ Raspberry Pi 4 ]
   ├─ ROS 2 core
   ├─ roboclaw_driver_node (C++)
   ├─ motion_supervisor_node (C++)
   ├─ sensor_i2c_node
   ├─ optical_flow_node
   ├─ camera / vision / NPU pipeline
   ├─ makerpi_bridge_node
   ├─ hmi_backend_node
   ├─ diagnostics + rosbag
   ├─ local browser kiosk
   └─ SSH server

[ RoboClaw 2x15A ]
   ├─ Packet Serial for control
   ├─ USB only for config / diagnostics when useful
   ├─ encoder feedback
   └─ motor power + regenerative protection considerations

[ Maker Pi / RP2040 ]
   ├─ USB CDC serial to Pi
   ├─ MicroPython
   ├─ buttons
   ├─ encoder
   ├─ OLED
   ├─ ToF / experimental sensors
   └─ optional local status display
```

---

## 19. Final Design Decision Summary

### Keep

- Pi as the single main controller
- ROS 2 as the integration layer
- local touchscreen HMI on Pi
- remote browser access
- Maker Pi as modular auxiliary I/O only

### Use

- **RoboClaw Packet Serial** for motor control
- **USB CDC** for Maker Pi
- **SPI** for optical flow when possible
- **I2C** for power and housekeeping sensors
- **CSI** for camera
- **C++** for critical control-side ROS 2 nodes

### Avoid

- making Maker Pi part of the critical control loop
- assuming RoboClaw natively supports RS-485
- relying on USB as the first production motor-control link without proving stability
- running a full Linux desktop all the time during normal operation
- assuming the RP2040 will behave like a normal always-mounted flash drive during normal MicroPython runtime

---

## 20. Recommended Next Implementation Steps

1. Bring up **Pi OS Lite + ROS 2**
2. Build a minimal **RoboClaw Packet Serial C++ node**
3. Validate one motor in closed-loop read/write with logging
4. Add the **custom HMI backend**
5. Run local browser HMI in kiosk mode
6. Add **Foxglove Bridge** for diagnostics
7. Add Maker Pi USB bridge with a minimal serial protocol
8. Add I2C power sensors and optical flow node
9. Add camera + NPU pipeline
10. Add watchdogs, fault handling, and startup sequencing

---

## 21. Source Notes

This architecture is based on the current RoboClaw datasheet and user manual behavior for Packet Serial, USB, and multi-unit wiring; current Raspberry Pi documentation for Pico / MicroPython / kiosk setup; and current Foxglove ROS 2 guidance for low-overhead live visualization.

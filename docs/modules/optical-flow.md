# Optical Flow Module Plan

## Scope and Goal

Primary objective: polish the near-complete optical-flow subsystem into a clean, repeatable, ROS2-ready module.

Current code root:

- `optical_flow/src`

## Interfaces

- Input:
  - SPI communication with PAA5100JE sensor
  - runtime arguments from CLI wrappers
  - calibration references (known velocity, known conditions)
- Output:
  - motion counts and derived flow vectors
  - benchmark/rate-sweep metrics
  - calibration summaries and ROS2 profile parameters
  - plots and optimization summaries

## Immediate Work Items (Detailed)

### A. Entrypoint and usability polish

- Keep `of_main.py` as the preferred operator entrypoint.
- Add concise usage comments and argument examples for local and SSH usage.
- Ensure command names and argument semantics are consistent across wrappers.

### B. `of_experimental.py` rationalization

- Keep only modes that are genuinely exploratory and not stable workflow commands.
- Redirect stable/production-like routines to dedicated scripts.
- Document explicit keep/deprecate list inside the module docs and source comments.

### C. LDR feedback loop for LED linearization

- Use Maker Pi ADC + LDR to measure visible output response.
- Run brightness sweeps and capture `(command_level, measured_light)` pairs.
- Build a lookup table (LUT) that maps user brightness percent to compensated LED command value.
- Integrate LUT as optional calibration profile input once validated.

### D. Neopixel ring integration

- Add external ring lighting control path for repeatable ambient tests.
- Keep ring control optional and isolated from core sensor read path.
- Document light-condition presets used during calibration captures.

## Calibration and Validation

- Smoke test baseline:
  - sensor init, comm check, and at least one valid motion read
- Performance baseline:
  - benchmark mode and stable-rate sweep
- Calibration baseline:
  - counts-to-velocity scale protocol
  - LED perceptual LUT capture protocol

## Logging and Outputs

- Keep CSV + JSON summaries from diagnostics and calibration scripts.
- Ensure graphing script reads latest outputs without manual path edits.
- Record profile outputs for ROS2 parameter export.

## ROS2 Readiness Contract

- define stable parameter names for poll rate, quality gates, and scale factors
- provide profile export path for node parameter files
- mark optional features (LUT, ring control) as runtime toggles

## Dependencies and Risks

- LDR + Maker Pi ADC wiring is pending hardware hookup.
- Sensor LED behavior is hardware non-linear and requires empirical compensation.
- Calibration transferability may depend on ambient conditions and sensor height.

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

## First Test Script

Run:

```bash
source .venv/bin/activate
python src/paa5100_first_test.py --help
```

Recommended sequence:

1. `python src/paa5100_first_test.py --mode info`
2. `python src/paa5100_first_test.py --mode motion --seconds 15`
3. `python src/paa5100_first_test.py --mode led --blink-count 6`

If LED control is not exposed in your local package version, motion mode still works and the script prints what method path was attempted.

## Logging Notes

The first test script writes CSV logs in `logs/` with:

- timestamp
- sequence index
- `dx`, `dy`
- `dt_s`
- estimated `vx_counts_s`, `vy_counts_s`
- `spi_ok`
- `led_action`
- error text (if present)

## Troubleshooting

- **`Invalid Product ID ... 0x00/0x00`**: SPI is not reading the chip (wrong CE line, bad wiring, SPI disabled, or no power). Check `ls /dev/spidev0.*`, then try `--spi-cs 0` and `--spi-cs 1`. The test script tries both CE lines by default unless you pass `--no-auto-cs`.
- Confirm SPI enabled in `raspi-config`.
- Verify sensor wiring and CS pin choice.
- Keep sensor at suitable height over textured surfaces.
- If values are mostly zero:
  - check illumination/surface texture
  - check rotation and orientation
  - verify library class is `PAA5100`


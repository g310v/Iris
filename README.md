# Iris - A polygon placement simulator

Displays as many non-overlapping polygons as possible on a canvas within a set time limit using my own (non-SAT) algorithm for detecting overlapping polygons.

The program:
- Loads polygon names and coordinates from an external file.
- Uses random shape, color, and coordinates for placement.
- Ensures polygons do **not** overlap, touch, or nest within each other.
- Uses a custom 
- Stops placement when the user-defined time limit expires.

## Features
- **Canvas:** Created with `turtle`, at 70% of screen size, centered on screen.
- **User Inputs:**
  - `Stretch Value` – Resize polygons (default: `1`).
  - `Duration` – Placement time limit in seconds (default: `5`).
  - `Random Seed` – Initialize random generator (default: `1`).
  - `Terminate` – Quit after run (`y` or `n`, default: `n`).

## Requirements
- Python 3.x
- `turtle` module (standard in Python)

## How to Run
```bash
python main.py
```
Follow prompts for configuration or press Enter to use defaults.

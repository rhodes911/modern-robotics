# Modern Robotics: Mechanics, Planning, and Control

This repository scaffolds your journey through the 6‑course Modern Robotics specialization (Lynch & Park). It provides a clean Python workspace, notes and labs structure, simulator integration, and stubs for kinematics/dynamics/planning code you’ll build as you go.

## Structure
- `setup/` – how to install CoppeliaSim and the Modern Robotics (MR) Python library.
- `mr/` – place the MR Python library here (see setup docs).
- `src/robotics/` – your code package (kinematics, dynamics, planning, control, mobile robots).
- `labs/` – course/week lab folders with starter READMEs.
- `notes/` – your notes per course.
- `simulators/coppeliasim/python/` – examples for ZMQ Remote API connection.
- `.vscode/` – editor settings for Python.

## Prerequisites
- Linear algebra, ODEs, basic physics (f=ma, torques), basic Python.
- Python 3.10+; optional MATLAB/Mathematica per course materials.
- CoppeliaSim (latest LTS) and its ZMQ Remote API client.
- Modern Robotics (MR) Python library (from modernrobotics.org).

## Quick Start (Windows PowerShell)
```powershell
# From repo root
python -m venv .venv; . .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# (Optional) Verify CoppeliaSim ZMQ Remote API client import
python - << 'PY'
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
print('ZMQ client OK')
PY

# Run the connection example (ensure CoppeliaSim is running)
python .\simulators\coppeliasim\python\connect_example.py
```

## Modern Robotics Library (MR)
- Download the MR Python library from http://modernrobotics.org and place it under `mr/` (see `setup/mr-library-setup.md`).
- Keep MR separate from your `src/` code to avoid accidental edits; import it explicitly in your labs as needed.

## CoppeliaSim
- Install CoppeliaSim; enable the ZMQ Remote API. See `setup/coppeliasim-setup.md`.
- Scenes used in the capstone are not included here; follow course instructions to download official scenes.

## Courses Mapping
- Course 1 – Foundations of Robot Motion (C‑spaces, twists/wrenches)
- Course 2 – Robot Kinematics (FK, IK, velocities, statics)
- Course 3 – Robot Dynamics (forward/inverse, trajectory generation)
- Course 4 – Motion Planning & Control (planning with obstacles, feedback control)
- Course 5 – Manipulation & Wheeled Mobile Robots
- Course 6 – Capstone (mobile manipulator planning/control)

## Notes
- This repo does not redistribute textbook content or official scenes. It links to the official sources and provides clean stubs and study scaffolding.

## Next Steps
1. Install requirements and MR library.
2. Work through course labs inside `labs/course-*` using `src/robotics` as your package.
3. Use `notes/course-*` for structured notes (templates in each folder README).
4. For the capstone, follow the course guide and use the CoppeliaSim example here as your starting point.

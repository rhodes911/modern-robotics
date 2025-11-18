# CoppeliaSim Setup (Windows)

1) Download and install CoppeliaSim (Edu/LTS) from https://www.coppeliarobotics.com/downloads.
2) Launch CoppeliaSim once to complete setup.
3) Enable ZMQ Remote API:
   - CoppeliaSim already ships with ZMQ remote API; no extra plugin is needed.
   - Ensure `zmqRemoteApi.dll` is present under `programming/zmqRemoteApi/clients/python`.
4) Python client:
   - Install `coppeliasim-zmqremoteapi-client` (see requirements.txt).
5) Test connection:
   - Start CoppeliaSim.
   - Run `python simulators/coppeliasim/python/connect_example.py` from repo root.

Troubleshooting
- If connection fails, check that CoppeliaSim is running and firewall allows localhost port 23000.
- If using a non-default port, set `CSIM_ZMQ_PORT` env var and update the example accordingly.

import time
import re
from pathlib import Path
import numpy as np

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import yaml


def connect_from_config():
    cfg_path = Path(__file__).parent.parent / "config" / "sim_config.yaml"
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    host = cfg.get("coppeliasim", {}).get("host", "127.0.0.1")
    port = cfg.get("coppeliasim", {}).get("port", 23000)
    client = RemoteAPIClient(host, port)
    sim = client.getObject("sim")
    return sim


def get_all_object_handles(sim):
    handles = []
    # sim.getObjects returns a list of all object handles
    try:
        handles = sim.getObjects()
    except Exception:
        pass
    return handles


def build_alias_map(sim, handles):
    alias_map = {}
    for h in handles:
        try:
            alias = sim.getObjectAlias(h)
            if alias:
                alias_map[alias] = h
        except Exception:
            continue
    return alias_map


def monitor_objects(duration_sec=5.0, sample_hz=10.0, pattern=r"^object_"):
    sim = connect_from_config()

    # Ensure simulation is running; if not, start it
    state = sim.getSimulationState()
    if state == sim.simulation_stopped:
        print("Starting simulation...")
        sim.startSimulation()
        # Wait for it to actually start
        while sim.getSimulationState() == sim.simulation_stopped:
            time.sleep(0.1)

    handles = get_all_object_handles(sim)
    alias_map = build_alias_map(sim, handles)
    tracked = {a: h for a, h in alias_map.items() if re.match(pattern, a)}

    if not tracked:
        print("No objects matching pattern found (pattern='{}').".format(pattern))
        return

    print(f"Tracking {len(tracked)} objects: {list(tracked.keys())}")

    interval = 1.0 / sample_hz
    samples = int(duration_sec * sample_hz)
    history = {alias: [] for alias in tracked.keys()}

    for i in range(samples):
        for alias, h in tracked.items():
            try:
                pos = sim.getObjectPosition(h, -1)  # world frame
                history[alias].append(pos)
            except Exception:
                history[alias].append(None)
        time.sleep(interval)

    print("\nSummary:")
    for alias, positions in history.items():
        none_count = sum(p is None for p in positions)
        if none_count == len(positions):
            print(f"- {alias}: handle invalid for all samples (object likely deleted at sim start).")
            continue
        first_valid = next((p for p in positions if p is not None), None)
        last_valid = next((p for p in reversed(positions) if p is not None), None)
        if first_valid is not None and last_valid is not None:
            dz = last_valid[2] - first_valid[2]
            min_z = min(p[2] for p in positions if p is not None)
            if min_z < -0.01:
                print(f"- {alias}: dropped below table (min z={min_z:.3f}) → falling through / no collision.")
            elif dz < -0.02:
                print(f"- {alias}: noticeable downward drift (Δz={dz:.3f}).")
            else:
                print(f"- {alias}: stable (z range [{min_z:.3f}, {max(p[2] for p in positions if p is not None):.3f}]).")
        else:
            print(f"- {alias}: intermittent validity (possible deletion/recreation).")

    print("\nRecommendations:")
    print("1. If objects disappear immediately: they were not part of the pre-sim scene. Build scene with simulation stopped, then save.")
    print("2. If z drops below desk: ensure desk thickness/position and respondable masks are correct.")
    print("3. Save scene after building: File > Save Scene, or call builder.save_scene().")
    print("4. Avoid rebuilding while simulation is running; stop sim before calling scene_builder.")
    print("5. If objects are deleted at sim start, confirm no cleanup script is attached to parent hierarchy.")


if __name__ == "__main__":
    monitor_objects()

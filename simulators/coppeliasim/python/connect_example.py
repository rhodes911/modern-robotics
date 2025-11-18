"""Minimal CoppeliaSim ZMQ Remote API connection example.

Ensure CoppeliaSim is running. This script connects, queries the sim version,
then disconnects.
"""
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def main() -> None:
    client = RemoteAPIClient()  # defaults to localhost:23000
    sim = client.getObject('sim')
    ver = sim.getInt32Param(sim.intparam_program_version)
    subver = sim.getInt32Param(sim.intparam_program_revision)
    print(f'CoppeliaSim version: {ver}.{subver}')


if __name__ == '__main__':
    main()

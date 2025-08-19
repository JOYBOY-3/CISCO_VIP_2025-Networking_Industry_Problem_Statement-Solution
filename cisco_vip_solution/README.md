# Cisco VIP 2025 – Networking Stream: Auto Topology + Validation + Simulation

This repository contains an internship-ready solution that:
- Parses router/switch-like config dumps and **auto-generates a hierarchical topology**
- **Validates** configuration quality (duplicate IPs per VLAN, VLAN label issues, gateway issues, MTU mismatches, loop detection)
- **Analyzes capacity** vs. traffic demands and recommends **load balancing**
- Provides a **Day‑1 simulation** (ARP / neighbor / OSPF-like discovery) and **fault injection**
- Implements **multithreading** (each node runs in its own thread)
- Uses **IPC** (TCP sockets) to exchange **metadata packets**
- Maintains **per-node logs & statistics** and supports **pause/resume**

> Designed to be **plagiarism-free**, clear, and extendable. Pure Python, no third‑party deps required.

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate  # (optional)
python3 src/main.py --conf ./sample/Conf --report ./output/report.json --run-sim --inject-failure R2-R3
```

- Topology/validation/capacity results are exported to `./output/`.
- Per-node simulation logs appear under `./output/logs/`.

## Project Structure
```
src/
  main.py
  config_parser.py
  graph.py
  validation.py
  capacity.py
  report.py
  simulator/
    __init__.py
    node.py
    ipc.py
    events.py
  utils/
    logger.py
sample/
  Conf/
    R1/config.dump
    R2/config.dump
    R3/config.dump
    # (Intentionally missing S1 to demonstrate missing-component detection)
```

## Configuration Format (Simplified)
Each `config.dump` is a **plain-text** file. Minimal supported lines:

```
hostname R1
interface Gig0/0 ip 10.0.0.1/24 vlan 10 mtu 1500 bw_mbps 1000 connected R2:Gig0/1
interface Gig0/1 ip 10.0.1.1/24 vlan 20 mtu 1400 bw_mbps 1000 connected R3:Gig0/0
gateway vlan10 10.0.0.254
endpoint PC1 vlan 10 app video peak_mbps 200 avg_mbps 50
```

- `connected <PeerName>:<PeerIf>` expresses physical adjacency.
- `endpoint` indicates load generators attached downstream to this node.
- **If a switch is referenced** (e.g., `S1:Gig1/0/1`) but its config file is **missing**, the tool flags it.

## What’s Implemented
- Deterministic parsing into structured nodes/links
- Graph build (routers / switches / endpoints) with hierarchy
- Validators:
  - Duplicate IPs per VLAN
  - VLAN sanity & cross-link mismatch
  - Gateway sanity (subnet membership check)
  - MTU mismatch across links
  - Loop detection (cycles)
  - Missing device configs
- Capacity analysis + Load‑balancing suggestions (secondary-path hints)
- Multithreaded Day‑1 simulation with TCP IPC (metadata packets)
- Fault injection (link disable), **pause/resume**

## Extend Ideas (to stand out)
- Real routing protocol state machine (OSPF LSAs, BGP sessions)
- Persist topology in Neo4j + web dashboard
- Predictive congestion using simple ML on node counters/logs
- Auto‑fix suggestions for IP pools/VLAN templates

---


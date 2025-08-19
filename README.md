# Cisco VIP 2025 – Networking Stream Problem Statement Solution
<h3><div>By Sourabh Kumar Gupta</div>
<div>AICTE ID : STU67619c38731771734450232</div>
<div>EMAIL ID : sourabhkrgupta720@gmail.com</div>
<div>University Enrollment ID : SBU2401957</div>
<div>Department : MCA</div>
<div>University : Sarala Birla University, Ranchi</div>
<div>Instructor : Dr. Pankaj K. Goswami & Mr. Bikram Pratap Singh</div>
</h3>


## 📌 Overview
This project implements a solution for the Cisco Virtual Internship Program (VIP) 2025 Networking Stream problem statement.  
The tool is designed to **automatically generate a hierarchical network topology** from router configuration files, **validate configurations**, **analyze traffic load vs. bandwidth**, and **simulate Day-1 and fault scenarios**.

---

## 🚀 Features Implemented
1. **Network Topology Generation**
   - Automatic parsing of router/switch config files (`config.dump`).
   - Extraction of interfaces, IPs, VLANs, MTUs, and bandwidths.
   - Graph-based hierarchical topology (Routers → Switches → Endpoints).

2. **Performance & Load Management**
   - Awareness of bandwidth and traffic demands.
   - Endpoint load analysis (video, IoT, VoIP, etc.).
   - Load balancing recommendations when links exceed capacity.

3. **Configuration Validation & Optimization**
   - Duplicate IP detection per VLAN.
   - VLAN mismatch detection.
   - Incorrect gateway detection.
   - MTU mismatch detection.
   - Missing components (e.g., missing switch configs).
   - Loop detection in topology.
   - Optimization suggestions (node aggregation, protocol recommendations).

4. **Simulation & Fault Injection**
   - Day-1 simulation (ARP, Neighbor discovery, OSPF-like hello messages).
   - Fault injection (link failures, MTU mismatch impacts).
   - Pause and resume simulation after config updates.
   - Multithreaded implementation (each router/switch as a thread).
   - Inter-process communication (TCP sockets for metadata packets).

5. **Implementation Architecture**
   - Pure Python implementation (standard library only).
   - Multithreading for network devices.
   - Logs maintained at node level.
   - JSON reports summarizing issues and recommendations.
   - Extensible design for ML or web dashboard integration.

---

## 📂 Project Structure
```
src/
  main.py              # Entry point
  config_parser.py     # Parses config files
  graph.py             # Builds topology graph
  validation.py        # Configuration validation checks
  capacity.py          # Load and bandwidth analysis
  report.py            # Report writer
  simulator/
    node.py            # Node thread implementation
    ipc.py             # IPC for metadata packet exchange
    events.py          # Pause/Resume events
  utils/
    logger.py          # Logger utility
sample/
  Conf/
    R1/config.dump
    R2/config.dump
    R3/config.dump
README.md              # Project overview
requirements.txt       # Dependencies (stdlib only)
```

---

## 🛠️ How to Run
1. Clone/Extract the repository.
2. Navigate to the project root directory.
3. Run with sample configs:
```bash
python3 src/main.py --conf ./sample/Conf --report ./output/report.json --run-sim --inject-failure R2-R3
```
4. Outputs:
   - `output/report.json` → Validation + capacity analysis results.
   - `output/sim/logs/` → Node-level logs with simulation events.

---

## 📊 Deliverables
- **Codebase (ZIP file)** with all modules.
- **Report (PDF)** explaining architecture and implementation.
- **Network diagram** (routers, switches, endpoints).
- **PowerPoint presentation** summarizing problem statement and solution.

---

## ✅ Fulfilled Requirements (from Cisco Problem Statement)
- [x] Automatic topology generation  
- [x] Awareness of bandwidth & traffic capacity  
- [x] Load balancing recommendations  
- [x] Detection of config issues (IPs, VLANs, gateways, MTU, loops, missing components)  
- [x] Day-1 simulation (ARP, neighbor discovery, OSPF)  
- [x] Fault injection (link failures, MTU mismatches)  
- [x] Pause & resume simulations  
- [x] Multithreading & IPC-based architecture  
- [x] Logs & statistics maintained at each node  



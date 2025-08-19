import argparse, os, json, ipaddress
from typing import Dict, Tuple
from utils.logger import Logger
from config_parser import load_configs
from graph import Graph
from validation import duplicate_ips, vlan_mismatch, mtu_mismatch, gateway_sanity, missing_configs, loop_detection
from capacity import summarize_endpoint_load, link_capacity_recommendations
from report import write_report
from simulator.node import SimNode
from simulator.events import SimEvents

def build_graph(nodes: Dict[str, Dict]) -> Graph:
    g = Graph()
    # Add nodes
    for n, cfg in nodes.items():
        ntype = 'router' if n.upper().startswith('R') else ('switch' if n.upper().startswith('S') else 'router')
        g.add_node(n, ntype, cfg)
    # Add edges based on 'connected' statements
    # We do not require the peer config to exist (so missing component can still create a ref edge)
    for n, cfg in nodes.items():
        for it in cfg.get('interfaces', []):
            conn = it.get('connected')
            if not conn or ':' not in conn: 
                continue
            peer, peer_if = conn.split(':', 1)
            bw = it.get('bw_mbps', 1000)
            mtu = it.get('mtu', 1500)
            vlan = it.get('vlan')
            # If peer exists, try to find the corresponding if for MTU/VLAN pair
            if peer in nodes:
                mtub = None; vlanb = None
                for jt in nodes[peer].get('interfaces', []):
                    if jt.get('name') == peer_if:
                        mtub = jt.get('mtu', 1500)
                        vlanb = jt.get('vlan')
                        bw = min(bw, jt.get('bw_mbps', bw))
                        break
                g.add_edge(n, peer, bw, (mtu, mtub), (vlan, vlanb))
            else:
                g.add_edge(n, peer, bw, (mtu, None), (vlan, None))
    return g

def simulate(g: Graph, outdir: str, inject_failure: str = None, run_seconds: int = 5):
    os.makedirs(outdir, exist_ok=True)
    # Assign ports
    base_port = 50000
    portmap = {name: base_port + i for i, name in enumerate(sorted(g.nodes.keys()))}
    # Neighbor map
    neigh = {n:{} for n in g.nodes}
    for (a,b) in g.edges.keys():
        if a in portmap and b in portmap:   # only connect if both nodes exist
            neigh[a][b] = portmap[b]
            neigh[b][a] = portmap[a]

    # Logs
    logs_dir = os.path.join(outdir, 'logs'); os.makedirs(logs_dir, exist_ok=True)
    # Start nodes
    events = SimEvents()
    nodes = {}
    for n, meta in g.nodes.items():
        log = Logger(logs_dir, n)
        nd = SimNode(n, meta['type'], portmap[n], neigh[n], log)
        nd.set_events(events)
        nodes[n] = nd
        nd.start()
    # Inject failure
    if inject_failure and '-' in inject_failure:
        a, b = inject_failure.split('-',1)
        if a in nodes and b in nodes:
            nodes[a].notify_link_failure(b)
            nodes[b].notify_link_failure(a)
    # Run
    import time
    time.sleep(run_seconds/2)
    # Pause/resume demo
    events.pause()
    time.sleep(0.5)
    events.resume()
    time.sleep(run_seconds/2)
    # Stop
    for nd in nodes.values():
        nd.stop()
    time.sleep(0.5)
    return os.path.abspath(outdir)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--conf', required=True, help='Path to Conf directory')
    ap.add_argument('--report', default='./output/report.json')
    ap.add_argument('--run-sim', action='store_true')
    ap.add_argument('--inject-failure', default=None, help='Format: NODEA-NODEB e.g., R2-R3')
    args = ap.parse_args()

    nodes = load_configs(args.conf)
    g = build_graph(nodes)

    # Validations
    issues = []
    issues += duplicate_ips(nodes)
    issues += vlan_mismatch(g.edges)
    issues += mtu_mismatch(g.edges)
    issues += gateway_sanity(nodes)
    issues += missing_configs(nodes)
    issues += loop_detection(g.has_cycle())

    # Capacity
    vlan_loads = summarize_endpoint_load(nodes)
    capacity_issues = link_capacity_recommendations(g.edges, vlan_loads)

    report = {
        'summary': {
            'nodes': list(g.nodes.keys()),
            'edges': [f'{a}-{b}' for (a,b) in g.edges.keys()],
        },
        'issues': issues,
        'capacity': {
            'vlan_loads': vlan_loads,
            'recommendations': capacity_issues
        }
    }

    write_report(args.report, report)

    outdir = os.path.dirname(args.report)
    if args.run_sim:
        simulate(g, outdir=os.path.join(outdir, 'sim'), inject_failure=args.inject_failure, run_seconds=6)

    print(f'Report written to: {args.report}')
    print('Done.')

if __name__ == '__main__':
    main()

from typing import Dict, List, Tuple
from collections import defaultdict

def summarize_endpoint_load(nodes: Dict[str, Dict]) -> Dict[int, Dict[str, int]]:
    # Return VLAN -> {'peak': int, 'avg': int}
    out = {}
    for n, cfg in nodes.items():
        for ep in cfg.get('endpoints', []):
            v = ep.get('vlan')
            if v is None:
                continue
            out.setdefault(v, {'peak':0,'avg':0})
            out[v]['peak'] += int(ep.get('peak_mbps',0))
            out[v]['avg']  += int(ep.get('avg_mbps',0))
    return out

def link_capacity_recommendations(edges: Dict[tuple, dict], vlan_loads: Dict[int, Dict[str,int]]):
    # Crude mapping: assume each link primarily carries traffic for its vlan (if any)
    recs = []
    for (a,b), meta in edges.items():
        va, vb = meta.get('vlan_pair', (None,None))
        bw = meta.get('bw_mbps', 1000)
        vlan = va if va is not None else vb
        if vlan is None:
            # no specific vlan; skip
            continue
        peak = vlan_loads.get(vlan, {}).get('peak', 0)
        if peak > bw:
            recs.append({
                'type': 'insufficient_link_capacity',
                'link': f'{a}-{b}',
                'vlan': vlan,
                'peak_demand_mbps': peak,
                'link_bw_mbps': bw,
                'recommendation': 'Activate secondary path for low-priority traffic or increase link capacity.'
            })
    return recs

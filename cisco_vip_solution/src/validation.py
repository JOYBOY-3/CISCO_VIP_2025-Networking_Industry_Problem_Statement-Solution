from typing import Dict, List, Tuple
from ipaddress import ip_network, ip_address
from collections import defaultdict

def build_ip_index(nodes: Dict[str, Dict]) -> Dict[Tuple[int,str], List[Tuple[str,str]]]:
    # key: (vlan, ip) -> list of (node, if)
    index = defaultdict(list)
    for n, cfg in nodes.items():
        for it in cfg.get('interfaces', []):
            ip = it.get('ip')
            vlan = it.get('vlan')
            if ip and vlan is not None:
                index[(vlan, ip)].append((n, it.get('name')))
    return index

def duplicate_ips(nodes: Dict[str, Dict]) -> List[Dict]:
    idx = build_ip_index(nodes)
    issues = []
    for k, lst in idx.items():
        if len(lst) > 1:
            issues.append({'type': 'duplicate_ip', 'vlan': k[0], 'ip': k[1], 'interfaces': lst})
    return issues

def vlan_mismatch(edges: Dict[tuple, dict]) -> List[Dict]:
    issues = []
    for (a,b), meta in edges.items():
        va, vb = meta.get('vlan_pair', (None,None))
        if va is not None and vb is not None and va != vb:
            issues.append({'type':'vlan_mismatch', 'link': f'{a}-{b}', 'vlan_a': va, 'vlan_b': vb})
    return issues

def mtu_mismatch(edges: Dict[tuple, dict]) -> List[Dict]:
    issues = []
    for (a,b), meta in edges.items():
        ma, mb = meta.get('mtu_pair', (None,None))
        if ma is not None and mb is not None and ma != mb:
            issues.append({'type':'mtu_mismatch', 'link': f'{a}-{b}', 'mtu_a': ma, 'mtu_b': mb})
    return issues

def gateway_sanity(nodes: Dict[str, Dict]) -> List[Dict]:
    issues = []
    for n, cfg in nodes.items():
        # Map VLAN -> list of subnets (from interfaces)
        vlan_subnets = {}
        for it in cfg.get('interfaces', []):
            ip_cidr = it.get('ip')
            vlan = it.get('vlan')
            if ip_cidr and vlan is not None:
                try:
                    net = ip_network(ip_cidr, strict=False)
                    vlan_subnets.setdefault(vlan, []).append(net)
                except:
                    pass
        for vlan, gw in cfg.get('gateways', {}).items():
            ok = False
            for net in vlan_subnets.get(vlan, []):
                if ip_address(gw) in net:
                    ok = True; break
            if not ok:
                issues.append({'type': 'gateway_out_of_subnet', 'node': n, 'vlan': vlan, 'gateway': gw})
    return issues

def missing_configs(nodes: Dict[str, Dict]) -> List[Dict]:
    # If an interface is connected to peer X:If and that peer name has no config file, flag it.
    known = set(nodes.keys())
    referenced = set()
    for n, cfg in nodes.items():
        for it in cfg.get('interfaces', []):
            conn = it.get('connected')
            if conn and ':' in conn:
                peer, _ = conn.split(':', 1)
                referenced.add(peer)
    missing = [p for p in referenced if p not in known]
    return [{'type':'missing_component','device': m} for m in missing]

def loop_detection(has_cycle: bool) -> List[Dict]:
    return [{'type':'loop_detected'}] if has_cycle else []

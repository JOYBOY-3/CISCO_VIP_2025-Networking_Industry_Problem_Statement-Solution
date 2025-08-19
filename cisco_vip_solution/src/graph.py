from typing import Dict, List, Tuple, Set
import ipaddress

class Graph:
    def __init__(self):
        self.nodes = {}   # name -> {'type': 'router'|'switch'|'endpoint', 'data': dict}
        self.edges = {}   # (a,b) sorted tuple -> {'bw_mbps': int, 'mtu_pair': (int,int), 'vlan_pair': (int,int)}
        self.vlans = set()

    def add_node(self, name: str, ntype: str, data: dict):
        self.nodes[name] = {'type': ntype, 'data': data}

    def add_edge(self, a: str, b: str, bw_mbps: int, mtu_pair, vlan_pair):
        key = tuple(sorted([a,b]))
        self.edges[key] = {'bw_mbps': bw_mbps, 'mtu_pair': mtu_pair, 'vlan_pair': vlan_pair}

    def neighbors(self, n: str) -> List[str]:
        out = []
        for (a,b) in self.edges:
            if a == n: out.append(b)
            elif b == n: out.append(a)
        return out

    def has_cycle(self) -> bool:
        visited: Set[str] = set()
        def dfs(v, parent):
            visited.add(v)
            for nb in self.neighbors(v):
                if nb == parent: 
                    continue
                if nb in visited or dfs(nb, v):
                    return True
            return False
        for n in self.nodes:
            if n not in visited:
                if dfs(n, None):
                    return True
        return False

from typing import Dict, List, Tuple, Optional
import os, ipaddress, re, json

def parse_config_file(path: str) -> Dict:
    data = {
        'hostname': None,
        'interfaces': [],  # list of dicts
        'gateways': {},    # vlan -> ip
        'endpoints': []    # list of dicts
    }
    with open(path, 'r') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'): 
                continue
            if line.startswith('hostname '):
                data['hostname'] = line.split()[1]
            elif line.startswith('interface '):
                # interface Gig0/0 ip 10.0.0.1/24 vlan 10 mtu 1500 bw_mbps 1000 connected R2:Gig0/1
                # very lenient parsing
                m_if = re.findall(r'interface\s+(\S+)', line)
                m_ip = re.findall(r'ip\s+(\S+)', line)
                m_vlan = re.findall(r'vlan\s+(\d+)', line)
                m_mtu = re.findall(r'mtu\s+(\d+)', line)
                m_bw  = re.findall(r'bw_mbps\s+(\d+)', line)
                m_conn= re.findall(r'connected\s+(\S+)', line)
                it = {
                    'name': m_if[0] if m_if else None,
                    'ip': m_ip[0] if m_ip else None,
                    'vlan': int(m_vlan[0]) if m_vlan else None,
                    'mtu': int(m_mtu[0]) if m_mtu else 1500,
                    'bw_mbps': int(m_bw[0]) if m_bw else 1000,
                    'connected': m_conn[0] if m_conn else None
                }
                data['interfaces'].append(it)
            elif line.startswith('gateway '):
                # gateway vlan10 10.0.0.254
                parts = line.split()
                # format: gateway vlan<id> <ip>
                if len(parts) == 3 and parts[1].startswith('vlan'):
                    try:
                        vlan_id = int(parts[1].replace('vlan','').strip())
                        data['gateways'][vlan_id] = parts[2]
                    except:
                        pass
            elif line.startswith('endpoint '):
                # endpoint PC1 vlan 10 app video peak_mbps 200 avg_mbps 50
                parts = line.split()
                ep = {'name': parts[1] if len(parts)>1 else None, 'vlan': None, 'app': None, 'peak_mbps': 0, 'avg_mbps': 0}
                if 'vlan' in parts:
                    ep['vlan'] = int(parts[parts.index('vlan')+1])
                if 'app' in parts:
                    ep['app'] = parts[parts.index('app')+1]
                if 'peak_mbps' in parts:
                    ep['peak_mbps'] = int(parts[parts.index('peak_mbps')+1])
                if 'avg_mbps' in parts:
                    ep['avg_mbps'] = int(parts[parts.index('avg_mbps')+1])
                data['endpoints'].append(ep)
    data['source_file'] = path
    return data

def load_configs(conf_root: str) -> Dict[str, Dict]:
    nodes = {}
    for name in os.listdir(conf_root):
        node_dir = os.path.join(conf_root, name)
        cfg_path = os.path.join(node_dir, 'config.dump')
        if os.path.isfile(cfg_path):
            cfg = parse_config_file(cfg_path)
            nodes[cfg['hostname'] or name] = cfg
    return nodes

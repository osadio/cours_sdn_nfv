from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

import networkx as nx


class TopologyDiscovery(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # List the event list should be listened.
    events = [
        event.EventSwitchEnter,
        event.EventSwitchLeave,
        event.EventPortAdd,
        event.EventPortDelete,
        event.EventPortModify,
        event.EventLinkAdd,
        event.EventLinkDelete,
        ]

    def __init__(self, *args, **kwargs):
        super(TopologyDiscovery, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        self.switches = []
        self.links = []
        self.hosts = {}
        self.arp_proxy_table = {}  # {ip:mac}
        self.network = nx.DiGraph() 

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                   ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(events)
    def get_topology(self, ev):
        switch_list = get_switch(self.topology_api_app, None)
        links_list = get_link(self.topology_api_app, None)

        self.switches  = [sw.dp.id for sw in switch_list]
        self.links = [(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]

        self.network.add_nodes_from(self.switches)
        self.network.add_edges_from(self.links)
        print("nodes:", list(self.network.nodes))
        print("links:", list(self.network.edges))
        print("\n")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if arp_pkt:
            arp_src_ip = arp_pkt.src_ip
            arp_src_mac = arp_pkt.src_mac
            self.add_host(arp_src_ip, datapath.id, in_port) 
            self.arp_proxy(msg, datapath, in_port, eth, arp_pkt)
        elif ip_pkt:
            ip_src_ip = ip_pkt.src
            ip_src_mac = eth.src
            ip_dst_ip = ip_pkt.dst
            self.add_host(ip_src_ip, datapath.id, in_port)
            if not(self.network.has_node(ip_src_ip) and self.network.has_node(ip_dst_ip)):
                return
            # Generate all simple paths in the graph G from source to target, 
            # starting from shortest ones
            shortest_paths = nx.shortest_simple_paths(self.network, ip_src_ip, ip_dst_ip)
            shortest_paths_list = list(shortest_paths)
            print(f"\nSimples paths determination for nodes: src={ip_src_ip} --> dst={ip_dst_ip}")
            print(shortest_paths_list)
            weight = "hop"
            self.route_packet(shortest_paths_list, weight, msg, datapath)

    def add_host(self, host_ip, sw_id, sw_port):
        # Do not update if previous infos do not change
        if self.network.get_edge_data(sw_id, host_ip) \
              and sw_port == self.network.get_edge_data(sw_id, host_ip)["port"]:
            return
        dst_mac_ = self.arp_proxy_table.get(host_ip)
        if dst_mac_:
            return 
        print(f"Adding host: {host_ip} in switch (id: {sw_id}, port: {sw_port})")
        if self.network.has_node(host_ip):
            self.network.remove_node(host_ip)
        self.network.add_node(host_ip)
        self.network.add_edge(host_ip, sw_id, port=sw_port)
        self.network.add_edge(sw_id, host_ip, port=sw_port)
        print(list(self.network.edges))

    def arp_proxy(self, msg, datapath, in_port, eth, arp_pkt):
        src_ip = arp_pkt.src_ip
        src_mac = arp_pkt.src_mac
        dst_ip = arp_pkt.dst_ip

        self.arp_proxy_table[src_ip] = src_mac

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        data = None
        out_port = None
        actions = []

        if arp_pkt.opcode == arp.ARP_REQUEST:
            dst_mac_ = self.arp_proxy_table.get(dst_ip)
            if not dst_mac_:
                data = msg.data
                out_port = ofproto.OFPP_FLOOD
            else:
                out_port = in_port
                pkt = packet.Packet()

                pkt.add_protocol(
                    ethernet.ethernet(
                        ethertype=eth.ethertype,
                        dst = eth.src,
                        src = dst_mac_
                    )
                )

                pkt.add_protocol(
                    arp.arp(
                        opcode=arp.ARP_REPLY,
                        src_mac= dst_mac_,
                        src_ip = dst_ip,
                        dst_mac= src_mac,
                        dst_ip = src_ip
                     )
                )

                pkt.serialize()
                data = pkt

            actions.append(datapath.ofproto_parser.OFPActionOutput(out_port))
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER,
                                in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data) 
            datapath.send_msg(out)

    def route_packet(self, shortest_path, weight, msg, datapath):
        #print(self.network.edges.data())
        path = None
        if shortest_path and weight == "hop":
            path = shortest_path[0]
        if not path:
            return
        print(f"Selected path (weight={weight}): + {path}")

        ip_src = path[0]
        ip_dst = path[-1]
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        for i in range(1, len(path)-1):
            if datapath.id == path[i]:
                previous_datapath_id = path[i-1] # host or switch 
                next_datapath_id = path[i+1]
                out_port = self.network.get_edge_data(datapath.id, next_datapath_id)["port"]
                in_port = self.network.get_edge_data(datapath.id, previous_datapath_id)["port"]
                #print(previous_datapath_id, (datapath.id, in_port, out_port), next_datapath_id)
                actions = [parser.OFPActionOutput(out_port)]
                match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip_src, ipv4_dst=ip_dst)
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, match, actions)
                    data = msg.data
                    out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=data)
                    datapath.send_msg(out)
                break

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
from ryu.lib import hub

from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

import time


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
        self.hosts = []
        # Start thread
        self.discover_thread = hub.spawn(self._discover)
        
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                   ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None,):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    priority=priority, match=match,
                                    instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(events)
    def get_topology(self, ev):
        """
             Get topology infos
        """
	# Get topology
        switch_list = get_switch(self.topology_api_app, None)
        links_list = get_link(self.topology_api_app, None)

        # Formatting topology
        self.switches  = [sw.dp.id for sw in switch_list]
        self.links = [(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in links_list]

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """
           Dectect new hosts via arp or ip packet
        """
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        arp_pkt = pkt.get_protocol(arp.arp)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        if arp_pkt:
            arp_src_ip = arp_pkt.src_ip
            mac = arp_pkt.src_mac
            link_host_sw = (arp_src_ip, datapath.id, {"port":in_port})
            if link_host_sw not in self.hosts:
                self.hosts.append(link_host_sw)
            link_sw_host = (datapath.id, arp_src_ip, {"port":in_port})
            if link_sw_host not in self.hosts:
                self.hosts.append(link_sw_host)
        elif ip_pkt:
            ip_src_ip = ip_pkt.src
            eth = pkt.get_protocols(ethernet.ethernet)[0]
            mac = eth.src
            link_host_sw = (ip_src_ip, datapath.id, {"port":in_port})
            if link_host_sw not in self.hosts:
                self.hosts.append(link_host_sw)
            link_sw_host = (datapath.id, ip_src_ip, {"port":in_port})
            if link_sw_host not in self.hosts:
                self.hosts.append(link_sw_host)
    def _discover(self):
        while True:
            print("\n")
            print("Switches :", self.switches)
            print("Links : ", self.links)
            print("Hosts : ", self.hosts)
            hub.sleep(5)

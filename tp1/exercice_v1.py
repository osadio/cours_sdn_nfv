from mininet.topo import Topo

class SwitchFabric( Topo ):
    def build( self ):
        # Add spine switches
        spine1 = self.addSwitch("spine1")
        spine2 = self.addSwitch("spine2")

        # Add leafs switches
        leaf1 = self.addSwitch("leaf1")
        leaf2 = self.addSwitch("leaf2")
        leaf3 = self.addSwitch("leaf3")

        # Add servers
        server1 = self.addHost("server1")
        server2 = self.addHost("server2")
        server3 = self.addHost("server3")

        # Create interconnect matrix
        self.addLink(spine1, leaf1)
        self.addLink(spine1, leaf2)
        self.addLink(spine1, leaf3)

        self.addLink(spine2, leaf1)
        self.addLink(spine2, leaf2)
        self.addLink(spine2, leaf3)

        # Create interconnect in Rack
        self.addLink(leaf1, server1)
        self.addLink(leaf2, server2)
        self.addLink(leaf3, server3)

topos = {"switch_fabric": (lambda: SwitchFabric() )}

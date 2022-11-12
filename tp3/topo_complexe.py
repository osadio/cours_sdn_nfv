from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):  
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add Switches
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")
        s4 = self.addSwitch("s4")
        s5 = self.addSwitch("s5")
        s6 = self.addSwitch("s6")
        s7 = self.addSwitch("s7")

        # Add Hosts
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        # Add links Host to Switch
        self.addLink(h1, s1)
        self.addLink(h2, s5)

        # Add links Switch to Swttch
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s5)
        self.addLink(s3, s4)
        self.addLink(s4, s5)
        self.addLink(s1, s6)
        self.addLink(s1, s6)
        self.addLink(s4, s6)
        self.addLink(s5, s6)
        self.addLink(s4, s7)
        self.addLink(s5, s7)


topos = { "mytopo": ( lambda: MyTopo() ) }

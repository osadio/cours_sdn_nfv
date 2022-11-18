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
        h1 = self.addHost("h1", ip="10.1.0.1/16")
        h2 = self.addHost("h2", ip="10.1.0.2/16")
        h3 = self.addHost("h3", ip="10.1.0.3/16")
        h4 = self.addHost("h4", ip="10.1.0.4/16")

        # Add links Host to Switch
        self.addLink(h1, s1, cls=TCLink, bw=300, delay=1)
        self.addLink(h2, s5, cls=TCLink, bw=300, delay=1)
        self.addLink(h3, s5, cls=TCLink, bw=300, delay=1)
        self.addLink(h4, s7, cls=TCLink, bw=300, delay=1)

        # Add links Switch to Swttch
        self.addLink(s1, s2, cls=TCLink, bw=100, delay=100)
        self.addLink(s1, s3, cls=TCLink, bw=1000, delay=50)
        self.addLink(s2, s5, cls=TCLink, bw=100, delay=40)
        self.addLink(s3, s4, cls=TCLink, bw=1000, delay=70)
        self.addLink(s4, s5, cls=TCLink, bw=1000, delay=25)
        self.addLink(s1, s6, cls=TCLink, bw=300, delay=15)
        self.addLink(s4, s6, cls=TCLink, bw=500, delay=23)
        self.addLink(s5, s6, cls=TCLink, bw=200, delay=90)
        self.addLink(s4, s7, cls=TCLink, bw=250, delay=750)
        self.addLink(s5, s7, cls=TCLink, bw=10, delay=60)


topos = { "mytopo": ( lambda: MyTopo() ) }

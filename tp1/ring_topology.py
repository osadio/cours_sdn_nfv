from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):  
     def build( self ):     
        # Add Switches
        s1 = self.addSwitch("s1", stp=True, failMode="standalone")
        s2 = self.addSwitch("s2", stp=True, failMode="standalone")
        s3 = self.addSwitch("s3", stp=True, failMode="standalone")
        s4 = self.addSwitch("s4", stp=True, failMode="standalone")

        # Add Hosts
        h1 = self.addHost("h1", ip="10.0.0.1")
        h2 = self.addHost("h2", ip="10.0.0.2")
        h3 = self.addHost("h3", ip="10.0.0.3")

        # Add links Host to Switch
        self.addLink(h1, s1, cls=TCLink, bw=1000, delay=1)
        self.addLink(h2, s2, cls=TCLink, bw=1000, delay=1)
        self.addLink(h3, s3, cls=TCLink, bw=1000, delay=1)

        # Add links Switch to Swttch
        self.addLink(s1, s2, cls=TCLink, bw=1000, delay=1)
        self.addLink(s2, s3, cls=TCLink, bw=10, delay=25)
        self.addLink(s3, s4, cls=TCLink, bw=100, delay=10)
        self.addLink(s4, s1, cls=TCLink, bw=1000, delay=1)

topos = { "mytopo": ( lambda: MyTopo() ) }

from mininet.topo import Topo

class MyTopo( Topo ):  
     def build( self ):
        # Add Switches
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        # Add Hosts
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        # Add links Host to Switch
        self.addLink(h1, s1)
        self.addLink(h2, s2)

        # Add links Switch to Swttch
        self.addLink(s1, s2)

topos = { "mytopo": ( lambda: MyTopo() ) }

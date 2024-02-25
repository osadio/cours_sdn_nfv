from mininet.topo import Topo

class MyTopo( Topo ):  
     def build( self ):
        # Add Switches
        s1 = self.addSwitch("s1")

        # Add Hosts
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")

        # Add links Host to Switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

topos = { "mytopo": ( lambda: MyTopo() ) }

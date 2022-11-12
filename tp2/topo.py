from mininet.topo import Topo
  
class MyTopo( Topo ):  
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )
        # Add hosts and switches
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")
        # Add switch 
        s1 = self.addSwitch("s1")
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
topos = { 'mytopo': ( lambda: MyTopo() ) }  

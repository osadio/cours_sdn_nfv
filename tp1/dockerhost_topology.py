#! /usr/bin/env python3

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

def myTopo():
    net = Containernet(controller=Controller, link=TCLink)

    info("*** Adding controller\n")
    net.addController("c0")

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")

    info("*** Adding hosts\n")
    h1 = net.addDockerHost(
        "h1", dimage="dev_test", ip="10.0.0.1", docker_args={"hostname": "h1"}
    )
    h2 = net.addDockerHost(
        "h2", dimage="dev_test", ip="10.0.0.2", docker_args={"hostname": "h2"}
    )

    info("*** Creating links\n")
    net.addLinkNamedIfce(s1, h1, bw=10, delay="100ms")
    net.addLinkNamedIfce(s1, h2, bw=10, delay="100ms")

    info("*** Starting network\n")
    net.start()

    info("*** Enter CLI\n")
    info("Use help command to get CLI usages\n")
    CLI(net)

    info("*** Stopping network")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    myTopo()


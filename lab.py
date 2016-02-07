#!/usr/bin/python
import os
import sys

import mininet.cli
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Node


def setup_mininet(controller):
    setLogLevel('info')

    net = Mininet(controller=None, autoSetMacs=True, listenPort=6634)
    net.addController('c0', controller=RemoteController, ip=controller, port=6653)

    try:
        net.start()
        return net
    except Exception, e:
        net.stop()
        raise e

def main():
    controller = os.environ.get('ODL')
    if controller == None:
        sys.exit("No controller set.")

    net = None
    try:
        net = setup_mininet(controller)
        if net is not None:
            mininet.cli.CLI(net)
    finally:
        if net is not None:
            net.stop()


if __name__ == '__main__':
    main()

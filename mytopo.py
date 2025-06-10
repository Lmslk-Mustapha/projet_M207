#!/usr/bin/python

## Example topology for containernet
## Created by Jorge Lopez & Jose Reyes 

"""
This is a simple example of a Containernet custom topology.
"""
from mininet.net import Containernet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import sys
import socket

# Set logging level to 'info' to display informational messages
setLogLevel('info')
# Create the main Containernet network object
net = Containernet()

# ============================================================================
# CONTROLLER SETUP
# ============================================================================

info('*** Adding controller\n')

# Add a remote SDN controller (ONOS) running on a separate container/host
# The controller manages the switches and defines forwarding rules

c1 = RemoteController( 'c1' , ip=socket.gethostbyname("onos"), port=6633)
net.addController(c1)

# ============================================================================
# CONTAINER AND HOST SETUP
# ====================================================================

info('*** Adding gateway container\n')

# Create a Docker container that acts as a network gateway
# This container will provide internet access to other nodes

gateway = net.addDocker('gateway', ip='10.10.1.1', mac='00:00:00:00:00:01', dimage="gateway")

info('*** Adding docker containers\n')

# Add a Docker container host running Ubuntu Trusty

h1 = net.addDocker('h1', ip='10.10.10.1', mac='9a:d8:73:d8:90:6a', dimage="ubuntu:trusty")
info('*** Adding hosts\n')
h2 = net.addHost('h2',  ip='10.10.20.1', mac='9a:d8:73:d8:90:6b')
h3 = net.addHost('h3',  ip='10.10.20.2', mac='9a:d8:73:d8:90:6c')

# Add traditional Mininet hosts (not Docker containers)

# ============================================================================
# SWITCH SETUP
# ====================================================================
info('*** Adding switches\n')

# Create OpenFlow switches that will be managed by the SDN controller

s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
s4 = net.addSwitch('s4')
s5 = net.addSwitch('s5')

info('*** Creating links\n')
# ============================================================================
# NETWORK TOPOLOGY LINKS
# ===================================================================

## Switch 1 (s1) links - Central hub connecting to all other switches
net.addLink( s1, s2, 2, 1 )
net.addLink( s1, s3, 3, 1 )
net.addLink( s1, s4, 4, 1 )
net.addLink( s1, s5, 5, 1 )

## Switch 2 (s2) links - Gateway switch providing external connectivity
net.addLink( s2, gateway, 21, 2)
net.addLink( s2, s3, 3, 2 )
net.addLink( s2, s4, 4, 2 )
net.addLink( s2, s5, 5, 2 )

## Switch 3 (s3) links - Container access switch
net.addLink( s3, s4, 4, 3 )
net.addLink( s3, h1, 11, 3 )

## Switch 4 (s4) links - Host access switch  
net.addLink (s4, s5, 5, 4) 
net.addLink (s4, h2, 12, 4) 
net.addLink (s4, h3, 13, 4) 


# ============================================================================
# NETWORK STARTUP AND CONFIGURATION
# ===================================================================
info('*** Starting network\n')
# Initialize and start all network components
net.start()

# ============================================================================
# GATEWAY CONFIGURATION FOR INTERNET ACCESS
# ============================================================================
# Configure the gateway container to act as a NAT router
# Enable IP masquerading for outbound traffic (NAT functionality)
gateway.cmd("iptables --table nat -A POSTROUTING -o eth0 -j MASQUERADE")
# Enable IP forwarding to allow the gateway to route packets between networks
gateway.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")

# ============================================================================
# ROUTING CONFIGURATION FOR HOSTS/CONTAINERS
# ============================================================================
# Configure all hosts and containers to use the gateway for internet access

# For Docker container h1:
h1.cmd("ip route del default")
h1.cmd("ip route add default via 10.10.1.1")
# For traditional hosts h2 and h3:
h2.cmd("ip route add default via 10.10.1.1")
h3.cmd("ip route add default via 10.10.1.1")

# ============================================================================
# INTERACTIVE MODE AND CLEANUP
# ====================================================================
info('*** Running CLI\n')
# Start the Mininet command line interface for interactive network testing
# Users can run commands like: pingall, iperf, sh, etc
CLI(net)
# Clean up and stop the network when CLI exits
net.stop()

import os
import sys
import time, random
import itertools

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import FIFOBroadcastPerfectChannel

from NODE.node import Node

# Due to the error in the library I cannot use "construct_winslab_topology_with_channels"
# Code is ported and modified from previous versions
def fully_connected_topology(topo, nodecount, nodetype, channeltype, context=None):
    topo.construct_winslab_topology_without_channels(nodecount, nodetype, context)
    pairs = list(itertools.permutations(range(nodecount), 2))
    topo.G.add_edges_from(pairs)
    edges = list(topo.G.edges)
    for k in edges:
      ch = channeltype(channeltype.__name__, str(k[0]) + "-" + str(k[1]))
      topo.channels[k] = ch

      topo.nodes[k[0]].D(ch)
      ch.U(topo.nodes[k[0]])

      topo.nodes[k[1]].D(ch)
      ch.U(topo.nodes[k[1]])

def main():
    N: int = 4
    waitTime = 200e-3 # 1ms
    messageCount = 100

    topo = Topology()
    fully_connected_topology(topo, N, Node, FIFOBroadcastPerfectChannel)

    topo.start()
    for i in range(messageCount):
        messagefrom, messageto = random.sample(range(N), 2)

        topo.nodes[messagefrom].unicast(messageto, f"MY MESSAGE #{i}")
        time.sleep(waitTime)

    time.sleep(5)

    totalMessageReceived = 0
    totalBytesReceived = 0
    for n in topo.nodes.values():
        totalMessageReceived += n.appl.receivedMessageCount
        totalBytesReceived += n.appl.receivedByteCount

    successRate = totalMessageReceived / messageCount
    failureRate = 1 - successRate
    throughput  = totalBytesReceived / (waitTime * messageCount)

    print("==================================================")
    print(f"Success Rate: {successRate*100}%")
    print(f"Failure Rate: {failureRate*100}%")
    print(f"Throughput  : {throughput*8 / 1e3} kbps")
    print("==================================================")

if __name__ == "__main__":
    main()

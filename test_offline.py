import os
import sys
import time, random
import threading

from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import FIFOBroadcastPerfectChannel

from NODE.node import Node

def main():
    N: int = 4
    waitTime = 0.1
    messageCount = 10

    topo = Topology()
    topo.construct_winslab_topology_with_channels(N, Node, FIFOBroadcastPerfectChannel)

    topo.start()
    for i in range(messageCount):
        messagefrom, messageto = random.sample(range(N), 2)

        topo.nodes[messagefrom].unicast(messageto, f"MY MESSAGE #{i}")
        time.sleep(waitTime)

    time.sleep(1)

    totalMessageReceived = 0
    totalBytesReceived = 0
    for n in topo.nodes.values():
        totalMessageReceived += n.appl.receivedMessageCount
        totalBytesReceived += n.appl.receivedByteCount

    successRate = totalMessageReceived / messageCount
    failureRate = 1 - successRate
    throughput  = totalBytesReceived / (waitTime * messageCount)

    print("==================================================")
    print(f"Success Rate: %{successRate*100}")
    print(f"Failure Rate: %{failureRate*100}")
    print(f"Throughput: {throughput*8} bps")
    print("==================================================")

if __name__ == "__main__":
    main()

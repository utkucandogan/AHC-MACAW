import os
import sys
import time, random

from adhoccomputing.Experimentation.Topology import Topology

from NODE.nodeUsrp import NodeUsrp

def main():
    N: int = 4
    waitTime = 10e-3 # 1ms
    messageCount = 100

    topo = Topology()
    topo.construct_winslab_topology_without_channels(N, NodeUsrp)

    topo.start()
    time.sleep(5)
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

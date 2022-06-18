With the increasing popularity of Ad-Hoc Networks, it is important to examine the capabilities of the possible designs. Our main purpose of this project is to implement MACAW, a MAC Protocol for a Ad-Hoc network environment and examine its characteristics using Usrp B210 devices. Main observations of this project is to implement MACAW in Python programming language and observe the success rate of messages under a simple DATA-ACK protocol and throughput of the system.

Introduction
============

MACAW is a MAC Protocol that is designed to work on a single channel wireless LAN @bharghavan1994macaw. The design itself is an improvement upon MACA in order to increase performance on wireless medium and increase the fairness of the system. Our purpose is to implement the given algorithm with modifications for using it under an Ad-Hoc network.

With the increasing popularity of Ad-Hoc networks, it is important to test its limits and try to improve what is possible. Trying to observe the performance under MACAW will give us some information about its feasibility.

Designing an Ad-Hoc Network itself is a hard problem. With a somewhat complex MAC, the problem becomes harder. Since there are not that many of resources for Ad-Hoc network simulations, we are limited within the terms of knowledge.

MACAW does not designed to work with an Ad-Hoc Network. Hence, there are some optimizations in its protocol that is special for an uplink-downlink model. In order to solve it, we have to change some elements of its design.

Our main approach is to use Ad Hoc Computing Framework that is designed by CengWins @ahc. It gives us an interface to design, simulate and test our network implementations. It has features such as

Background and Related Work
===========================

Background
----------

MACA is a slotted MAC that consists of RTS, CTS and DATA packets. RTS (Request to Send) packet is send when a node wants to initialize a link. Upon receiving an RTS packet, if the node is not deferred, it will send a CTS (Clear to Send) packet. When sender receives the CTS packet, it will send the DATA packet. Another node who hears a CTS will enter into deferred mode in order to solve the hidden terminal problem @karn1990maca. MACA uses binary exponential backoff for resend attempts in order to reduce collisions.

MACAW is a MAC protocol that is an extension of MACA. Besides the RTS, CTS and DATA; it adds RRTS, DS and ACK packets as well. When a node receives CTS, instead of directly sending DATA, it first sends DS (Data Sending) packet to announce to its neighbors that the RTS-CTS handshake is successful. This gives the symmetric information and helps to solve the exposed terminal problem @bharghavan1994macaw. When a node receives a DATA packet successfully, it sends back an ACK packet. If a node receives an RTS packet while it is in deferred mode, after deferral period is over, it sends back an RRTS (Request to RTS) in order to signal the sender that it is now clear to initiate an exchange.

Instead of using binary exponential backoff, MACAW uses a different model called MILD (Multiplicative Increase, Linear Decrease) @bharghavan1994macaw. While binary exponential backoff resets its backoff counter when a connection becomes successful, MILD decreases the backoff counter linearly. In order to balance that, multiplication factor is decreased to 1.5 from 2. MACAW also adds a field in packet headers in order to share backoff values. in order to prevent starvation and detect congestion.

AHC library is an event-driven library for simulating and testing Ad-Hoc networks @ahc. Each layer is implemented as a different component which has its own events and event handlers. Components are connected either from top, bottom or as a peer. Events can be send through these connections.

Main Contribution
=================

Main contribution of this project is to implement MACAW for AHC library and analyze its performance using Usrp devices.

Results and Discussion
======================

Methodology
-----------

AHC library has “GenericMAC” class which can be inherited for implementing MACAW. This class has a queue which we used for buffering the packets that are coming from the upper layer. Then each packet can be processed one by one. MACAW is implemented as a state machine. There are three main events that can change our state: packet receiving, slot start and timeout. Packet receiving event implements two rulesets that are defined in MACAW definition @bharghavan1994macaw. These are control rules and deferral rules. Control rules handle main packet exchanges that our node participates and deferral rules handle overhearding other packets. Exchange initialization is started at slot starts. Hence it is implemented in frame handler. Finally, timeouts and backoffs are handled in timeout events.

MACAW uses a method for backoff copying that is designed for a uplink-downlink communication system where each node holds the backoff value of their neighbors @bharghavan1994macaw. However, for an Ad-Hoc system, this method is inefficient as each node can be mobile and multiple communication links may be established. Hence, we have choose to implement a simple copying method where a node copies the other nodes’ backoff value, if their backoff values are smaller than its value.

Our design is tested by two different methods. First one is a simulation where a perfect channel is used. Second one uses real devices for test. There are four main parameters for our experiments. First one is the slot length where we take it between 100ms and 1s. Message generation rate is how many messages are generated per second. We tried 1Hz and 100Hz. Third, we have a parameter for how many messages will be generated for simulation. We tried for 10 and 100. Message origin and destination selected randomly among each node. Finally, we have a parameter for wait time to allow for emptying the buffers.

Our tests uses four nodes as there are only four Usrp devices in our possession.

Results
-------

We have run our simulations experiments with different parameters. For simulations with fitting parameters, we can get 100% success rate and this verifies that our design works correctly. However, for experiments with real devices, we have very low success rate, among them the most successful one has 10% success rate. All results can be seen in

Discussion
----------

Our results are not expected as we have 100% success rate in simulations but have nearly 0% for experiments. Simulation results shows us that our implementation is correct. However, it was not expected that there will be very high packet loss for experiments. One prediction is the method of how the library is implemented. MACAW control packets must be short in order to avoid collisions. Bharghavan states that they have taken the RTS packet as 30 bytes long @bharghavan1994macaw. However, due to the usage of python classes as packets, AHC packets are much longer than the desired value. This may cause problems in our experimentations.

Conclusion
==========

In conclusion, we have tried to show the feasibility of using MACAW for Ad-Hoc networks. We have implemented MACAW protocol using AHC library and verified that it is working using simulations. However, we have failed to show that it can be used in real life due to the failure in our experiments. In a future work, we can try to examine our implementation for any errors or we may try to find better equipments to improve performance.

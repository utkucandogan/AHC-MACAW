from .node import Node

from adhoccomputing.Generics import *
from adhoccomputing.Networking.PhysicalLayer.UsrpB210OfdmFlexFramePhy import  UsrpB210OfdmFlexFramePhy

class NodeUsrp(Node):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None,
                 num_worker_threads=4, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        
        # SUBCOMPONENTS
        #sdrconfig = SDRConfiguration(freq =2484000000.0, bandwidth = 20000000, chan = 0, hw_tx_gain = 76, hw_rx_gain = 20, sw_tx_gain = -12.0)
        self.phy  = UsrpB210OfdmFlexFramePhy("UsrpB210OfdmFlexFramePhy", componentinstancenumber, usrpconfig=sdrconfig, topology=topology)
        self.components.append(self.phy)

        # Clear connections before reconnecting
        self.mac.connectors.clear()
        self.connectors.clear()

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.mac.connect_me_to_component(ConnectorTypes.UP, self.appl)
        self.mac.connect_me_to_component(ConnectorTypes.DOWN, self.phy)

        self.phy.connect_me_to_component(ConnectorTypes.UP, self.mac)
        self.phy.connect_me_to_component(ConnectorTypes.DOWN, self)

        self.connect_me_to_component(ConnectorTypes.UP, self.phy)

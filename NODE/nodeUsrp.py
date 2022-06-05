from .node import Node

from adhoccomputing.Generics import *
from adhoccomputing.Networking.PhysicalLayer.UsrpB210OfdmFlexFramePhy import  UsrpB210OfdmFlexFramePhy
from adhoccomputing.Networking.MacProtocol.CSMA import MacCsmaPPersistent, MacCsmaPPersistentConfigurationParameters

class NodeUsrp(Node):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None,
                 num_worker_threads=4, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        
        # SUBCOMPONENTS
        macconfig     = MacCsmaPPersistentConfigurationParameters(0.5)

        self.phy = UsrpB210OfdmFlexFramePhy("UsrpB210OfdmFlexFramePhy", componentinstancenumber, topology=topology)
        self.mac = MacCsmaPPersistent("MacCsmaPPersistent", componentinstancenumber, configurationparameters=macconfig, topology=topology, uhd=self.phy.ahcuhd)
        
        self.components.append(self.mac)
        self.components.append(self.phy)

        # Clear connections before reconnecting
        self.appl.connectors.clear()
        self.connectors.clear()

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.mac)
        
        self.mac.connect_me_to_component(ConnectorTypes.UP, self.appl)
        self.mac.connect_me_to_component(ConnectorTypes.DOWN, self.phy)

        self.phy.connect_me_to_component(ConnectorTypes.UP, self.mac)
        self.phy.connect_me_to_component(ConnectorTypes.DOWN, self)

        self.connect_me_to_component(ConnectorTypes.UP, self.phy)

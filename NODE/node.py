from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, ConnectorTypes, GenericMessageHeader, GenericMessage
from adhoccomputing.Networking.MacProtocol.CSMA import MacCsmaPPersistent, MacCsmaPPersistentConfigurationParameters

import MAC
from MAC.MACAW import MACAW, MACAWConfigurationParameters

from .appl import ApplicationLayer, ApplicationLayerEventTypes, ApplicationLayerMessageHeader

class Node(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None,
                 num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        # SUBCOMPONENTS
        self.appl = ApplicationLayer("ApplicationLayer", componentinstancenumber, topology=topology)
        self.mac  = MACAW("MACAWMACLayer",componentinstancenumber, topology=topology)

        self.components.append(self.appl)
        self.components.append(self.mac)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.mac)

        self.mac.connect_me_to_component(ConnectorTypes.UP, self.appl)
        self.mac.connect_me_to_component(ConnectorTypes.DOWN, self)

        self.connect_me_to_component(ConnectorTypes.UP, self.mac)
        
    def on_init(self, eventobj: Event):
        pass

    def on_message_from_top(self, eventobj: Event):
        # Transparent sending for channel simulations
        #print(f"[{self.componentname}.{self.componentinstancenumber}] Sending to channel...")
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

    def on_message_from_bottom(self, eventobj: Event):
        # Transparent sending for channel simulations
        #print(f"[{self.componentname}.{self.componentinstancenumber}] Getting from channel...")
        self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))

    def unicast(self, messageto: int, data):
        header = GenericMessageHeader(None, self.componentinstancenumber, messageto)
        packet = GenericMessage(header, data)
        self.appl.send_self(Event(self, ApplicationLayerEventTypes.UNICAST, packet))

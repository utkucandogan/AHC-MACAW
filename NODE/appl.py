# This file implements a TCP-like layer for an application layer example

import time
from enum import Enum

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, GenericMessageHeader, GenericMessage

# define your own message types
class ApplicationLayerMessageTypes(Enum):
    DATA   = "DATA"
    ACK    = "ACK"

# define your own message header structure
class ApplicationLayerMessageHeader(GenericMessageHeader):
    pass

class ApplicationLayerEventTypes(Enum):
    UNICAST = "unicast"

class ApplicationLayer(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None,
                 num_worker_threads=4, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        
        self.eventhandlers[ApplicationLayerEventTypes.UNICAST] = self.on_unicast
        self.processingTime = 0.1

        self.receivedMessageCount = 0
        self.receivedByteCount = 0

    def on_message_from_top(self, eventobj: Event):
        print(f"Unexpected Event at {self.componentname}.{self.componentinstancenumber}, "
              f"sending down eventcontent={eventobj.eventcontent}\n")
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))
    
    def on_message_from_bottom(self, eventobj: Event):
        if eventobj.eventcontent.header.messageto != self.componentinstancenumber:
            # Message is not for us, ignore
            return

        print(f"[{self.componentname}.{self.componentinstancenumber}] Received a packet:")
        print(f"\tFrom: {eventobj.eventcontent.header.messagefrom}")
        print(f"\tType: {eventobj.eventcontent.header.messagetype}")

        typ = eventobj.eventcontent.header.messagetype
        if typ == ApplicationLayerMessageTypes.DATA:
            print(f"\tData: \"{eventobj.eventcontent.payload}\"")
            print(f"Acknowledging data...")

            header = ApplicationLayerMessageHeader(ApplicationLayerMessageTypes.ACK, self.componentinstancenumber, eventobj.eventcontent.header.messagefrom)
            time.sleep(self.processingTime)
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))

            self.receivedMessageCount += 1
            self.receivedByteCount += len(str(eventobj.eventcontent.payload))

        elif typ == ApplicationLayerMessageTypes.ACK:
            print(f"\tMessage sent.")
            
        else:
            print(f"\t[Error] Event Type is unknown! Received packet will not be processed.")
            return
    
    def on_unicast(self, eventobj: Event):
        print(f"[{self.componentname}.{self.componentinstancenumber}] Sending Unicast message:")
        print(f"\tTo: {eventobj.eventcontent.header.messageto}")
        print(f"\tContent: \"{eventobj.eventcontent.payload}\"")

        self.idle = False
        self.conn = eventobj.eventcontent.header.messageto
        self.data = eventobj.eventcontent.payload

        time.sleep(self.processingTime)
        header = ApplicationLayerMessageHeader(ApplicationLayerMessageTypes.DATA, self.componentinstancenumber, self.conn)
        self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, eventobj.eventcontent.payload)))

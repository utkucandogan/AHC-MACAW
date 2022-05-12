# This file implements a TCP-like layer for an application layer example

import os
import sys
import time
from enum import Enum

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, GenericMessageHeader, GenericMessage

# define your own message types
class ApplicationLayerMessageTypes(Enum):
    SYN    = "SYN"
    SYNACK = "SYNACK"
    DATA   = "DATA"
    ACK    = "ACK"
    END    = "END"

# define your own message header structure
class ApplicationLayerMessageHeader(GenericMessageHeader):
    pass

class ApplicationLayerEventTypes(Enum):
    UNICAST = "unicast"

class ApplicationLayer(GenericModel):
    def __init__(self, componentName, componentInstanceNumber, context=None, configurationParameters=None,
                 num_worker_threads=1, topology=None):
        super().__init__(componentName, componentInstanceNumber, context, configurationParameters, num_worker_threads, topology)
        self.eventhandlers[ApplicationLayerEventTypes.UNICAST] = self.on_unicast

    def end_connection(self):
        self.idle = True
        self.conn = None
        self.data = None

        self.waitingSYNACK = False
        self.waitingDATA = False
        self.waitingACK = False
        self.waitingEND = False

    def on_init(self, eventobj: Event):
        self.timeout = 1000
        self.maxTrial = 10

        self.idle = True
        self.conn = None
        self.data = None

        self.waitingSYNACK = False
        self.waitingDATA = False
        self.waitingACK = False
        self.waitingEND = False
        
    def on_message_from_top(self, eventobj: Event):
        print(f"Unexpected Event at {self.componentname}.{self.componentinstancenumber}, "
              f"sending down eventcontent={eventobj.eventcontent}\n")
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))
    
    def on_message_from_bottom(self, eventobj: Event):
        print(f"[{self.componentname}.{self.componentinstancenumber}] Received a packet:")
        print(f"\tFrom: {eventobj.eventcontent.header.messagefrom}")
        print(f"\tType: {eventobj.eventcontent.header.messagetype}")

        typ = eventobj.eventcontent.header.messagetype
        if typ == ApplicationLayerMessageHeader.SYN:
            if not self.idle:
                print(f"\tLayer is busy. Received packet will not be processed.")
                return
            print(f"\tAccepting connection request.")
            header = ApplicationLayerMessageHeader(ApplicationLayerMessageHeader.SYNACK, self.componentinstancenumber, self.conn)

            self.waitingDATA = True
            for _ in range(self.maxTrial):
                self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))
                time.sleep(self.timeout)
                if not self.waitingDATA: break
            else:
                print(f"[{self.componentname}.{self.componentinstancenumber}] Timeout.")
                self.end_connection()
        
        elif tpy == ApplicationLayerMessageHeader.SYNACK:
            if not self.waitingSYNACK or eventobj.eventcontent.header.messagefrom != self.conn:
                print(f"\tAstray packet. Received packet will not be processed.")
                return
            print(f"\tConnection established. Sending data...")
            header = ApplicationLayerMessageHeader(ApplicationLayerMessageHeader.DATA, self.componentinstancenumber, self.conn)

            self.waitingSYNACK = False
            self.waitingACK = True
            for _ in range(self.maxTrial):
                self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, self.data)))
                time.sleep(self.timeout)
                if not self.waitingACK: break
            else:
                print(f"[{self.componentname}.{self.componentinstancenumber}] Timeout.")
                self.end_connection()

        elif typ == ApplicationLayerMessageHeader.DATA:
            if not self.waitingDATA or eventobj.eventcontent.header.messagefrom != self.conn:
                print(f"\tAstray packet. Received packet will not be processed.")
                return
            print(f"\tData: \"{eventobj.eventcontent.payload}\"")
            print(f"Acknowledging data...")
            header = ApplicationLayerMessageHeader(ApplicationLayerMessageHeader.ACK, self.componentinstancenumber, self.conn)

            self.waitingDATA = False
            self.waitingEND = True
            for _ in range(self.maxTrial):
                self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))
                time.sleep(self.timeout)
                if not self.waitingEND: break
            else:
                print(f"[{self.componentname}.{self.componentinstancenumber}] Timeout.")
                self.end_connection()
        
        elif typ == ApplicationLayerMessageHeader.ACK:
            if not self.waitingACK or eventobj.eventcontent.header.messagefrom != self.conn:
                print(f"\tAstray packet. Received packet will not be processed.")
                return
            print(f"\tMessage sent. Closing connection...")
            header = ApplicationLayerMessageHeader(ApplicationLayerMessageHeader.END, self.componentinstancenumber, self.conn)

            self.waitingACK = False
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))
            self.end_connection()

        elif typ == ApplicationLayerMessageHeader.END:
            if not self.waitingEND or eventobj.eventcontent.header.messagefrom != self.conn:
                print(f"\tAstray packet. Received packet will not be processed.")
                return
            print(f"\tConnection closed.")

            self.waitingEND = False
            self.end_connection()
        
        else:
            print(f"\t[Error] Event Type is unknown! Received packet will not be processed.")
            return
    
    def on_unicast(self, eventobj: Event):
        print(f"[{self.componentname}.{self.componentinstancenumber}] Sending Unicast message:")
        print(f"\tTo: {eventobj.eventcontent.header.messageto}")
        print(f"\tContent: \"{eventobj.eventcontent.payload}\"")

        self.isSending = True
        self.sendingTo = eventobj.eventcontent.header.messageto
        self.message   = eventobj.eventcontent.payload

        header = ApplicationLayerMessageHeader(ApplicationLayerMessageHeader.SYN, self.componentinstancenumber, self.sendingTo)

        self.waitingSYNACK = True
        for _ in range(self.maxTrial):
            self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, None)))
            time.sleep(self.timeout)
            if not self.waitingSYNACK: break
        else:
            print(f"[{self.componentname}.{self.componentinstancenumber}] Timeout.")
            self.end_connection()

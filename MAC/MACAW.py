import time
import random
from enum import Enum
from threading import Timer, Lock

from adhoccomputing.Generics import Event, EventTypes, GenericMessage, GenericMessageHeader
from adhoccomputing.Networking.MacProtocol.GenericMAC import GenericMac, GenericMacEventTypes

import MAC
from MAC.backoff import MILDBackoffCounter
from MAC.config  import MACAWConfigurationParameters
from MAC.header  import MACAWMessageHeader
from MAC.timeout import MACAWTimeout

class MACAWMessageType(Enum):
    RTS     = "RTS"
    RRTS    = "RRTS"
    CTS     = "CTS"
    DS      = "DS"
    DATA    = "DATA"
    ACK     = "ACK"

class MACAWState(Enum):
    IDLE        = "IDLE"
    CONTENDs    = "CONTENDs"
    CONTENDr    = "CONTENDr"
    WFCTS       = "WFCTS"
    WFCTS_Retry = "WFCTS_Retry"
    WFContend   = "WFContend"
    WFDS        = "WFDS"
    WFData      = "WFData"
    WFACK       = "WFACK"
    QUIET       = "QUIET"

class MACAW(GenericMac):
    def __init__(self, componentname, componentinstancenumber, context=None,
                 configurationparameters=MACAWConfigurationParameters(), num_worker_threads=4, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.slotTime = configurationparameters.slotTime

        self.state      = MACAWState.IDLE
        self.stateMutex = Lock()
        self.backoff    = MILDBackoffCounter(configurationparameters.backoffMin, configurationparameters.backoffMax)
        self.timer      = MACAWTimeout(self.slotTime, self.backoff, self.timeout)

        self.prevACK = None
        self.sequencenumber = 0
        self.packetOnProcess = None
        self.reservedSender = self.componentinstancenumber # Temporary

    ## Packet send
    def send_data(self, header, data):
        self.send_down(Event(self, EventTypes.MFRT, GenericMessage(header, data)))

    def send_control(self, header):
        self.send_data(header, None)

    def get_rts_header(self):
        return MACAWMessageHeader(MACAWMessageType.RTS, self.componentinstancenumber, self.packetOnProcess.header.messageto,
            self.sequencenumber, 5, self.backoff.get())

    def get_rrts_header(self):
        return MACAWMessageHeader(MACAWMessageType.RRTS, self.componentinstancenumber, self.reservedSender,
            -1, 5, self.backoff.get())

    ## Event Handlers
    def on_message_from_top(self, eventobj: Event):
        print(f"[{self.componentname}.{self.componentinstancenumber}] Received a packet from top:")
        self.framequeue.put_nowait(eventobj.eventcontent)
    
    def on_message_from_bottom(self, eventobj: Event):
        received  = eventobj.eventcontent
        messageTo = received.header.messageto
        typ       = received.header.messagetype

        self.stateMutex.acquire()

        if messageTo == self.componentinstancenumber:
            print(f"[{self.componentname}.{self.componentinstancenumber}] Received a packet:")
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tFrom: {received.header.messagefrom}")
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tType: {received.header.messagetype}")

            # Control rules except for sending
            if self.state == MACAWState.IDLE and typ == MACAWMessageType.RTS:
                # Check if already received
                if self.prevACK is not None and \
                    self.prevACK.get_messageid(False) == received.header.get_messageid(True):
                    print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending ACK...")

                    # Re-send ack
                    self.send_control(self.prevACK)

                else:
                    print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending CTS...")

                    # send CTS
                    header = received.header.create_response(MACAWMessageType.CTS)
                    self.send_control(header)

                    # set timer
                    self.state = MACAWState.WFDS
                    self.timer.start_wait()

            elif (self.state == MACAWState.CONTENDs or self.state == MACAWState.CONTENDr or self.state == MACAWState.WFCTS_Retry) \
                    and typ == MACAWMessageType.RTS:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending CTS...")

                self.timer.reset()

                # send CTS
                header = received.header.create_response(MACAWMessageType.CTS)
                self.send_control(header)

                # set a timer
                self.state = MACAWState.WFDS
                self.timer.start_wait()

            elif (self.state == MACAWState.WFCTS or self.state == MACAWState.WFACK) and typ == MACAWMessageType.CTS:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending DS & DATA...")

                # clear the timer
                self.timer.reset()

                # send DS
                header = received.header.create_response(MACAWMessageType.DS)
                self.send_control(header)

                time.sleep(self.slotTime) # In order to ensure DS send first

                # send data
                header = received.header.create_response(MACAWMessageType.DATA)
                self.send_data(header, self.packetOnProcess)

                self.state = MACAWState.WFACK
                self.timer.start_backoff()

            elif self.state == MACAWState.WFDS and typ == MACAWMessageType.DS:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tPreparing to listen...")

                self.timer.reset()

                # set a timer
                self.state = MACAWState.WFData

                deferral = received.header.expectedduration
                self.timer.start_slot(deferral+1)

            elif self.state == MACAWState.WFData and typ == MACAWMessageType.DATA:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending ACK...")

                # clear the timer
                self.timer.reset()

                # get data and send it to upper layer
                self.send_up(Event(self, EventTypes.MFRB, received.payload))

                # send ACK
                header = received.header.create_response(MACAWMessageType.ACK)
                self.send_control(header)

                self.state = MACAWState.IDLE

            elif self.state == MACAWState.WFACK and typ == MACAWMessageType.ACK:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tEnding connection...")

                # clear the timer
                self.timer.reset()
                self.state = MACAWState.IDLE

                # decrease backoff
                self.backoff.decrease()

            elif self.state == MACAWState.QUIET and typ == MACAWMessageType.RTS:
                self.state = MACAWState.WFContend
                self.reservedSender = received.header.messagefrom

            elif self.state == MACAWState.IDLE and typ == MACAWMessageType.RRTS:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending RTS...")

                # send RTS
                header = MACAWMessageHeader(MACAWMessageType.RTS, self.componentinstancenumber,
                    self.packetOnProcess.header.messageto, self.sequencenumber, 5, self.backoff.get())
                self.send_control(header)
                
                self.state = MACAWState.WFCTS
            else:
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tUnknown packet. Discarding...")
                print(f"[{self.componentname}.{self.componentinstancenumber}] \tMy state is <{self.state}>")
                pass

        else:
            print(f"[{self.componentname}.{self.componentinstancenumber}] Overheard a packet.")

            if self.state == MACAWState.IDLE or self.state == MACAWState.CONTENDr or self.state == MACAWState.CONTENDs:
                # Deferral Rules
                if typ == MACAWMessageType.RTS or typ == MACAWMessageType.RRTS:
                    if self.timer.isRunning(): self.timer.reset()

                    # set timer until CTS
                    self.state = MACAWState.QUIET
                    self.timer.start_slot(1)

                elif typ == MACAWMessageType.RRTS:
                    if self.timer.isRunning(): self.timer.reset()

                    # set timer until RTS&CTS
                    self.state = MACAWState.QUIET
                    self.timer.start_slot(2)

                elif typ == MACAWMessageType.DS or typ == MACAWMessageType.CTS:
                    if self.timer.isRunning(): self.timer.reset()

                    # Copy backoff if it is smaller
                    backoff = received.header.senderbackoff
                    if backoff < self.backoff.get():
                        self.backoff.set(backoff)
                        self.backoff.decrease() # Since the other one will also decrease

                    # get expected duration
                    deferral = received.header.expectedduration

                    # set timer until data&ack
                    self.state = MACAWState.QUIET
                    self.timer.start_slot(deferral+1)

                else:
                    pass

        self.stateMutex.release()
    
    def handle_frame(self):
        if self.state == MACAWState.IDLE and not self.framequeue.empty():
            print(f"[{self.componentname}.{self.componentinstancenumber}] Going to Contend...")

            # get from queue
            self.packetOnProcess = self.framequeue.get_nowait()

            # set a random timer
            self.state = MACAWState.CONTENDs
            self.timer.start_contend()

        # Continuously trigger handle_frame
        Timer(self.slotTime, lambda s: s.send_self(Event(s, GenericMacEventTypes.HANDLEMACFRAME, None)), [self]).start()

    def timeout(self):
        print(f"[{self.componentname}.{self.componentinstancenumber}] Timeout...")

        self.stateMutex.acquire()

        if self.state == MACAWState.WFContend:
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tGoing to Contend...")
            # set a random timer
            self.state = MACAWState.CONTENDr
            self.timer.start_contend()

        elif self.state == MACAWState.CONTENDs:
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending RTS to <{self.packetOnProcess.header.messageto}>...")

            # Send RTS
            self.sequencenumber += 1

            header = self.get_rts_header()
            self.send_control(header)
            
            self.state = MACAWState.WFCTS
            self.timer.start_backoff()

        elif self.state == MACAWState.CONTENDr:
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tSending RRTS to <{self.reservedSender}>...")

            # send RRTS
            header = self.get_rrts_header()
            self.send_control(header)

            self.state = MACAWState.IDLE

        elif self.state == MACAWState.WFCTS or self.state == MACAWState.WFACK:
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tRe-sending RTS to <{self.packetOnProcess.header.messageto}>...")

            # Backoff and resend RTS
            self.backoff.increase()
            
            header = self.get_rts_header()
            self.send_control(header)

            self.state = MACAWState.WFCTS_Retry
            self.timer.start_backoff()

        else:
            print(f"[{self.componentname}.{self.componentinstancenumber}] \tGoing IDLE.")

            self.state = MACAWState.IDLE

        self.stateMutex.release()
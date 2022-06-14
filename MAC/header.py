from adhoccomputing.Generics import GenericMessageHeader

class MACAWMessageHeader(GenericMessageHeader):
    def __init__(self, messagetype, messagefrom, messageto, sequencenumber, expectedduration, senderbackoff):
        super().__init__(messagetype, messagefrom, messageto, sequencenumber)
        self.expectedduration = expectedduration
        self.senderbackoff = senderbackoff

    def get_messageid(self, amIreceiver):
        return f"{self.messagefrom if amIreceiver else self.messageto}-{self.sequencenumber}"

    def create_response(self, messageType):
        return MACAWMessageHeader(messagetype = messageType, messagefrom = self.messageto, messageto = self.messagefrom,
            sequencenumber = self.sequencenumber, expectedduration = self.expectedduration,
            senderbackoff = self.senderbackoff)
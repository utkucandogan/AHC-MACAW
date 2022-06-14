class MACAWConfigurationParameters:
    def __init__(self, slotTime = 10e-3, backoffMin = 2, backoffMax = 64):
        self.slotTime = slotTime
        self.backoffMin = backoffMin
        self.backoffMax = backoffMax

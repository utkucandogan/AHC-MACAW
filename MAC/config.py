class MACAWConfigurationParameters:
    def __init__(self, slotTime = 50e-3, backoffMin = 2, backoffMax = 64, verbose = False):
        self.slotTime = slotTime
        self.backoffMin = backoffMin
        self.backoffMax = backoffMax
        self.verbose = verbose

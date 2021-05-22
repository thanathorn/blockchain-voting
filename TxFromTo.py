class TxFromTo:
    def __init__(self, address, value):
        self.address = address
        self.value = int(value)

    def __str__(self):
        return "{address:{0}, value{1}}".format(self.address, self.value)

    def getAddress(self):
        return self.address

    def getValue(self):
        return self.value

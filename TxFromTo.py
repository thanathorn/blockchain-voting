import json


class TxFromTo:
    def __init__(self, address, value):
        if address is None or value is None:
            self.address = None
            self.value = None
        else:
            self.address = address
            self.value = int(value)

    def __str__(self):
        return json.dumps({"address": self.address, "value": self.value})

    def getAddress(self):
        return self.address

    def getValue(self):
        return self.value

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

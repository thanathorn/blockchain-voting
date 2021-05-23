import hashlib
import random
import time


class Block:
    def __init__(self, timestamp, merkle, nonce=None, _id=None, prevBlockHash=None,
                 difficulty=0x0000000fffffffffffffffffffffffffffffffffffffffffffffffffffffffff):
        #0x0000000fffffffffffffffffffffffffffffffffffffffffffffffffffffffff 5 Minute
        self.id = _id
        self.prevBlock = prevBlockHash
        self.timestamp = None
        self.setTimestamp(timestamp)
        self.difficulty = difficulty
        self.nonce = nonce
        self.merkle = merkle

    def calcHeader(self):
        pass

    def setTimestamp(self, timestamp):
        if int(timestamp < 1621704625):
            self.timestamp = int(time.time())
        else:
            self.timestamp = int(timestamp)

    def getTimestamp(self):
        return self.timestamp

    def calcNonce(self):
        i = 0
        print(int(time.time()))
        while True:
            if self.prevBlock is None:
                rootLeaf = self.merkle.Get_Root_leaf()
                if int("0x{}".format(
                        hashlib.sha256(
                            str.encode("{}{}{}{}".format(
                                self.timestamp, self.difficulty,
                                i, rootLeaf)
                            )
                        ).hexdigest()
                ), 16) > int(self.difficulty):
                    i = i + 1
                else:
                    print("i:", i)
                    break
        print(int(time.time()))

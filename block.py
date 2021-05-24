import hashlib
import random
import time

from merkle import MerkleTree
from transaction import Transaction


class Block:
    def __init__(self, timestamp, merkle, nonce=None, _id=None, prevBlockHash=None,
                 difficulty=0x000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff):
        # 0x0000000fffffffffffffffffffffffffffffffffffffffffffffffffffffffff 5 Minute
        self.id = _id
        self.prevBlock = prevBlockHash
        self.timestamp = None
        self.setTimestamp(timestamp)
        self.difficulty = difficulty
        self.nonce = nonce
        self.merkle = merkle

    def calcHeader(self):
        rootLeaf = self.merkle.Get_Root_leaf()
        if self.prevBlock is None:
            self.id = int("0x{}".format(
                hashlib.sha256(
                    str.encode("{}{}{}{}".format(
                        self.timestamp, self.difficulty,
                        self.nonce, rootLeaf)
                    )
                ).hexdigest()), 16)
        else:
            self.id = int("0x{}".format(
                hashlib.sha256(
                    str.encode("{}{}{}{}{}".format(self.prevBlock,
                                                   self.timestamp, self.difficulty,
                                                   self.nonce, rootLeaf)
                               )
                ).hexdigest()
            ), 16)

    def setTimestamp(self, timestamp):
        if int(timestamp < 1621704625):
            self.timestamp = int(time.time())
        else:
            self.timestamp = int(timestamp)

    def getTimestamp(self):
        return self.timestamp

    def calcNonce(self):
        i = 0
        # print(int(time.time()))
        rootLeaf = self.merkle.Get_Root_leaf()
        while True:
            if self.prevBlock is None:
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
                    self.nonce = i
                    self.calcHeader()
                    # print(int(time.time()))
                    return self.nonce
                    # break
            else:
                if int("0x{}".format(
                        hashlib.sha256(
                            str.encode("{}{}{}{}{}".format(self.prevBlock,
                                                           self.timestamp, self.difficulty,
                                                           i, rootLeaf)
                                       )
                        ).hexdigest()
                ), 16) > int(self.difficulty):
                    i = i + 1
                else:
                    self.nonce = i
                    self.calcHeader()
                    # print(int(time.time()))
                    return self.nonce

    def verifyNonce(self):
        rootLeaf = self.merkle.Get_Root_leaf()
        if self.prevBlock is None:
            if int("0x{}".format(
                    hashlib.sha256(
                        str.encode("{}{}{}{}".format(
                            self.timestamp, self.difficulty,
                            self.nonce, rootLeaf)
                        )
                    ).hexdigest()
            ), 16) < int(self.difficulty):
                return True
        else:
            if int("0x{}".format(
                    hashlib.sha256(
                        str.encode("{}{}{}{}{}".format(self.prevBlock,
                                                       self.timestamp, self.difficulty,
                                                       self.nonce, rootLeaf)
                                   )
                    ).hexdigest()
            ), 16) < int(self.difficulty):
                return True
        return False

    def blockHash(self):
        rootLeaf = self.merkle.Get_Root_leaf()
        if self.prevBlock is None:
            return int("0x{}".format(
                hashlib.sha256(
                    str.encode("{}{}{}{}{}".format(self.id,
                        self.timestamp, self.difficulty,
                        self.nonce, rootLeaf)
                    )
                ).hexdigest()), 16)
        else:
            return int("0x{}".format(
                hashlib.sha256(
                    str.encode("{}{}{}{}{}{}".format(self.id, self.prevBlock,
                                                   self.timestamp, self.difficulty,
                                                   self.nonce, rootLeaf)
                               )
                ).hexdigest()
            ), 16)

    def verifyBlock(self):
        # verify tx
        txCheckList = []
        for node in self.merkle:
            if isinstance(node, Transaction):
                txCheckList.append(node)
        tree = MerkleTree(txCheckList)
        tree.create_tree()
        if self.merkle.Get_Root_leaf() != tree.Get_Root_leaf():
            return False

        if not self.verifyNonce():
            return False

        return True


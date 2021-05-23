import base64
import json
import hashlib
import TxFromTo
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key


class Transaction:
    def __init__(self):
        self.hash = None
        self.type = None
        self.timestamp = None
        self.tx_from = TxFromTo.TxFromTo(address=None, value=None)
        self.tx_to = TxFromTo.TxFromTo(address=None, value=None)
        self.signature = None

    def setTimestamp(self, timestamp):
        if int(timestamp < 1621704625):
            self.timestamp = int(time.time())
        else:
            self.timestamp = int(timestamp)

    def getTimestamp(self):
        return self.timestamp

    def setType(self, type):
        if (type not in ["transfer", "create"]):
            self.type = None
        else:
            self.type = type

    def getType(self):
        return self.type

    def setTxFrom(self, address, value):
        tx = TxFromTo.TxFromTo(address, value)
        self.tx_from = tx

    def getTxFrom(self):
        return self.tx_from

    def setTxTo(self, address, value):
        tx = TxFromTo.TxFromTo(address, value)
        self.tx_to = tx

    def getTxTo(self):
        return self.tx_to

    def getSignature(self):
        return self.signature

    def signSignature(self, privateKey):
        pk = load_pem_private_key(privateKey.encode(), None, default_backend())
        signature = pk.sign(
            str.encode("{}{}{}{}".format(self.type, self.timestamp, self.tx_from, self.tx_to)),
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256()
        )
        self.signature = base64.b64encode(signature).decode('ascii')

    def hashTx(self):
        self.hash = hashlib.sha256(str.encode("{}{}{}{}{}".format(self.type, self.timestamp, self.tx_from, self.tx_to,
                                                                  self.signature))).hexdigest()

    def getHash(self):
        return self.hash

    def verify(self):
        try:
            if self.type != "create":
                pubkey = load_pem_public_key(self.tx_from.getAddress().encode(), default_backend())
                pubkey.verify(
                    base64.b64decode(self.signature.encode('ascii')),
                    str.encode("{}{}{}{}".format(self.type, self.timestamp, self.tx_from, self.tx_to)),
                    padding.PSS(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH,
                    ),
                    hashes.SHA256()
                )
            if (hashlib.sha256(str.encode("{}{}{}{}{}".format(self.type, self.timestamp, self.tx_from, self.tx_to,
                                                              self.signature))).hexdigest() != self.hash):
                return False
            return True
        except InvalidSignature:
            print("Invalid Signature")
            return False

    def __str__(self):
        return json.dumps({
            "hash": self.hash,
            "type": self.type,
            "timestamp": self.timestamp,
            "tx_from": self.tx_from.toJson(),
            "tx_to": self.tx_to.toJson(),
            "signature": self.signature
        })

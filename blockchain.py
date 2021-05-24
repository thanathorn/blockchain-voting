import pickle
import time

from block import Block
from merkle import MerkleTree
from transaction import Transaction


class Blockchain:
    def __init__(self):
        try:
            self.chain = pickle.load(open("blockchain.bin", 'rb'))
            print("[*] Blockchain: opening chain file")
        except Exception as e:
            print(e)
            print("[*] Blockchain: creating chain file")
            self.chain = []
            self.createGenesisBlock()

    def last_block(self):
        return self.chain[-1]

    def addBlock(self, block):
        if len(self.chain) == 0:
            self.chain.append(block)
            return 1
        if block.prevBlock != self.last_block().blockHash():
            print("Cannot add block to chain: Previous block hash mismatch")
            return False
        else:
            self.chain.append(block)
            return  True

    def save(self):
        blockchainFile = open('blockchain.bin', 'wb')
        print("Chain saved")
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(self.chain, blockchainFile, pickle.HIGHEST_PROTOCOL)

    def createGenesisBlock(self):
        prikey = """-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAobve3e/IvnBc/mqAoNURIF++ZVMNnih3Nf3UkC2QSpQn/vIj
NRZHXb4Vq9lgpnvAezbakbAr/w1CrVPjCA4sjywFC93h4TC8oJKuzVmDBWdJxbs4
BRTwSzeerCtGXv+ZRvsSP9WIKXFX0II5BUo+50uaASMvF+mBzNs75XDqZ9ooeYX6
jwCchSAIa2kpCV/rtuT2ABGVNVY62VmJ+d4WFfXDEilDpUwZ0exPA3sqObJqqYjl
JyQekvlEDpJvLshz6B2wBu7slqmn9s07it83emqC4kP7HPO3Di9ggPly/KLa47Ge
+jpjM+Nq6yiGrqHiTI0ZqLf+ncoKgIRqK3Di3QIDAQABAoIBAQCauGY5PJV3EXj0
7h/FPG9Y4B79QZmqbp20afI6R0xc/CTS8QMbWwfEtv52WsrqGUMG3G/1pWpBYYci
1zg+UYjxIjRlqMrYqc4ZcpmE2xfLSIc7gKHTwrcpzbiejfuRD8WrMK7BoF3U/5f5
YUp5NBC/JgTbB7SalIjW1/gRw5aK55OShqE9ECRqhwIiIsOpTqLkwscGV5r3SAt4
Fll5WJ2TcjivLqApsK5Adv9y2mp/FCaV4M8sursLXkiCtgIOsuiic4Ezz6TdOyH2
OVj8qhoRl0oHxF/Um6Z3whRykKZILdgobyZWmomCH6gfcQL8Rz0pNx7QcPl6imDi
sjbvwHyBAoGBANd1E0ZRjMyKMBp7CiFGD/JFag6JU3Q/23PefLI6/GakDLkPEEID
2Od+2VtJJsvltlzIVOpY1UCE/QCRON/KXD7zVNZVaHqrnvZmYcWgc1wiIKvSyrAK
W0jis8K53/SvyIbdDkd+z4n3eMZKMjF/2+AYjNikSlpqaTi7zvB9jaYhAoGBAMAq
2a0699z0P0Kqf7asVa2JtiUcxxkxaNlDpLha0igx48NUR6CsH9AD7VubSgc53IAK
FDYz781GryjwuGHuMjPp2mXFwiO2QvXMTK0ReScrDoQUiAPaPH7U/CTuVt2J8z0j
W8Nay/XWJ5x8gJP0F47Ee19QE1xgzQxuqoBB7K09AoGAQPm5mlc1kumJoDLC1039
uR5d4YxgcopfcA4EpOtM+tc2TwjP6limrQmAGxtwa8UWvdxcX1/yz8ZLVkR1Vmf8
ca+IQir3mybuhXhSu/qrT3mrSKYFIhm9dbmIZI0RkQUCAEnh6IXBqOXMsl/lyy+3
61j8AMlq8uFsYgOhYL08XoECgYEArfJbxfX5xXUGCleBcZ5/k61zRhbNll1mVjxn
z0TOtPmr/PS+PY9w4H+djG19zhqvIOt+ri3HJJ6WEU4M6QCPSvSk77jZ6i+iXxKG
WabWbwEHi8F1+V7Dod8zOk7QLIshtbba6nO26hnnEzyTutmZtW7fakB2tgkdsuI9
zglertUCgYEA0ltjY4olXDY6eEdL5WvDY39gfT03+6taGYbruB1DDNHaEq92fHUZ
I/7IHd+2fobwNMT1AgnWyDSbNtWYHFqffL+lsOQqf3P6ZEIpE2AubdWh7LnD4sG2
aG+BwzHO0W6PIJH1cxq4kN1Dw4cG1e/cjQDNXAhVcf9lnv8ZLRbDmJE=
-----END RSA PRIVATE KEY-----
"""
        tx = Transaction()
        tx.setType("create")
        tx.setTxTo(address="", value=0)
        tx.setTimestamp(time.time())
        tx.signSignature(privateKey=prikey)
        tx.hashTx()

        tree = MerkleTree([tx])
        tree.create_tree()

        block = Block(1621767060, tree)

        block.calcNonce()

        self.addBlock(block)
        self.save()
        print("[*] Blockchain: genesis block added")


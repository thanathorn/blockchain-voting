import base64
import json
import pickle
import time
import zmq

from blockchain import Blockchain
from transaction import Transaction
from merkle import MerkleTree
from block import Block
pubkey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAobve3e/IvnBc/mqAoNUR
IF++ZVMNnih3Nf3UkC2QSpQn/vIjNRZHXb4Vq9lgpnvAezbakbAr/w1CrVPjCA4s
jywFC93h4TC8oJKuzVmDBWdJxbs4BRTwSzeerCtGXv+ZRvsSP9WIKXFX0II5BUo+
50uaASMvF+mBzNs75XDqZ9ooeYX6jwCchSAIa2kpCV/rtuT2ABGVNVY62VmJ+d4W
FfXDEilDpUwZ0exPA3sqObJqqYjlJyQekvlEDpJvLshz6B2wBu7slqmn9s07it83
emqC4kP7HPO3Di9ggPly/KLa47Ge+jpjM+Nq6yiGrqHiTI0ZqLf+ncoKgIRqK3Di
3QIDAQAB
-----END PUBLIC KEY-----
"""
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
pubkey2 = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCHSggLHNSmkyInd0mR3vXw3Irv
eMZuVMheTcn2paJX8beslXWU49FhixRLhRtmip0BFGSYNsfvR/kqf7gwZ7vjvcKk
iBDgYBgs8iYp0gzSZZjMQIkkaNG51urTXWOSTd4sWLvXYoRX8bpmg9+C6Ku0aJmV
d/QFrIdq/KfFsosWWQIDAQAB
-----END PUBLIC KEY-----
"""
prikey2 = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCHSggLHNSmkyInd0mR3vXw3IrveMZuVMheTcn2paJX8beslXWU
49FhixRLhRtmip0BFGSYNsfvR/kqf7gwZ7vjvcKkiBDgYBgs8iYp0gzSZZjMQIkk
aNG51urTXWOSTd4sWLvXYoRX8bpmg9+C6Ku0aJmVd/QFrIdq/KfFsosWWQIDAQAB
AoGAVGMiN0RJhIm8QR/QHRQVFqOKaitMot9xiBk/hAD3DaIxro4fpLqiDRUCmMSz
PbfyjQzaXnO1LJUZX6ABFPhvoou3x5AUIC4/knbQ7Ogde+8FfXQ3cBybLbzNVbWI
oHWbvw/55RxUekuOkZaqRfAu0ZPxkjb5UMPLIhv9rX16hfECQQC8nYAY9ymkYV/X
UmkBd8Jg/0kdfMyxlr3eFYQ6TztCDA0Oj7yN9rQsC610i3qX0an7AtC1xGUeGvhN
D1mLaFXFAkEAt59mranigUZpd8PHklaGrkOG2Jhsga9pkFhL1ND7W21LLAgdRW3X
eWa5LWniabvTg8T1fS8L4WHPDiiiyovbhQJAI65wA0kOuagqJ2PRtZNgVFU3EbsA
RkBMHu1XHGjMvwvklHKgqwKWxxZWdAvG312smG3J6fkDYBSeEIXs3LCaOQJBAIX7
naRiLZA+nH5zMJAq6qMFSsOIlMQcBl74znw+8OnJWeyLDzC18V/4AG6OsFKOZsvj
T21Egtq1z6t5Iy+/1TECQQCop15TbRCaYtsJTF9jI0sGiNaVKzQASqNCEXM2nqoD
jb2QDv+k4ONP1o3wPvNq4ocbHZOvzfx+pO/M58EVCkMK
-----END RSA PRIVATE KEY-----
"""

tx = Transaction()
tx.setType("create")
# tx.setTxFrom(address=pubkey, value="2000")
tx.setTxTo(address="", value=0)
tx.setTimestamp(time.time())
tx.signSignature(privateKey=prikey)
tx.hashTx()

tx2 = Transaction()
tx2.setType("transfer")
tx2.setTxFrom(address=pubkey, value="2000")
tx2.setTxTo(address=pubkey2, value="2000")
tx2.setTimestamp(1621767050)
tx2.signSignature(privateKey=prikey)
tx2.hashTx()

tx3 = Transaction()
tx3.setType("transfer")
tx3.setTxFrom(address=pubkey, value="2000")
tx3.setTxTo(address=pubkey2, value="2000")
tx3.setTimestamp(1621767055)
tx3.signSignature(privateKey=prikey)
tx3.hashTx()

# my_pickle_string = pickle.dumps(tx)
# # print(my_pickle_string)
# f = open("../currentBlock.txt", "w")
# f.write(base64.b64encode(my_pickle_string).decode('ascii'))
# f.close()
#
# with open('../currentBlock.txt', 'rb') as f:
#     x = f.read()
#     abc = pickle.loads(base64.b64decode(x))
#     print(abc.getTimestamp())
# context = zmq.Context()
# context.setsockopt(zmq.RCVTIMEO, 3000)
# #  Socket to talk to server
# print("Connecting to master server???")
# socket = context.socket(zmq.REQ)
#
# socket.connect("tcp://localhost:30002")
# #  Do 10 requests, waiting each time for a response
# for request in range(100):
#     print("Sending request %s ???" % request)
#     print(my_pickle_string)
#     socket.send(my_pickle_string)
#
#     #  Get the reply.
#     try:
#         message = socket.recv()
#         print("Received reply %s [ %s ]" % (request, message))
#     except:
#         socket.close()
#         socket = context.socket(zmq.REQ)
#         context.setsockopt(zmq.RCVTIMEO, 3000)
#         socket.connect("tcp://localhost:30002")
tree = MerkleTree([tx, tx2, tx3])
tree.create_tree()
merkle = tree.Get_past_transacion()
txCheckList = []
for node in merkle:
    if isinstance(node, Transaction):
        txCheckList.append(node)
tree2 = MerkleTree(txCheckList)
tree2.create_tree()
print(tree2.Get_Root_leaf())
print(tree.Get_Root_leaf())
    # print(node)
chain = Blockchain()

block = Block(1621767060, tree, prevBlockHash=chain.last_block().blockHash())
block.calcNonce()
print(block.verifyNonce())
print(block.difficulty)
#
#
# chain.addBlock(block)
# chain.save()
# with open('data.pickle', 'wb') as f:
#     # Pickle the 'data' dictionary using the highest protocol available.
#     pickle.dump(block, f, pickle.HIGHEST_PROTOCOL)
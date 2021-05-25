import hashlib
import time

from blockchain import Blockchain
from transaction import Transaction
import requests

clear = lambda: print('\n' * 100)

chain = Blockchain()


def getBalanceByOwner(address=None):
    global chain
    balance = 0
    txs = []
    for block in chain.chain:
        for merkleNode in block.merkle.Get_past_transacion():
            if isinstance(merkleNode, Transaction):
                if merkleNode.type == "create":
                    if merkleNode.tx_to.address == address:
                        txs.append(merkleNode)
                        balance += merkleNode.tx_to.value
                elif merkleNode.type == "transfer":
                    if merkleNode.tx_to.address == address:
                        txs.append(merkleNode)
                        balance += merkleNode.tx_from.value
                    elif merkleNode.tx_from.address == address:
                        txs.append(merkleNode)
                        balance -= merkleNode.tx_from.value
    return balance


questions = requests.get('http://127.0.0.1:8000/master/voter/question')
questions = questions.json()
clear()
j = 1

for question in questions:
    i = 0
    print("Question {} : {}".format(j, question['question']['question']))
    for ans in question['answers']:
        hashVal = hashlib.sha224(ans['answer'].encode()).hexdigest()
        print ("{}. {} ({}) ได้คะแนน {} คะแนน".format(i+1, ans['answer'], hashVal, getBalanceByOwner(hashVal)))
        i = i+1
    j = j + 1

time.sleep(3)
j = 1

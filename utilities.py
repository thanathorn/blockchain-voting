import hashlib
import json
import pickle
import socket
import time

import requests
import zmq

from blockchain import Blockchain
from helper import printLog
from transaction import Transaction
clear = lambda: print('\n' * 100)
masterIP = "127.0.0.1"
chain = Blockchain()


def masterAddressListener():
    global masterIP
    masterServerAddrSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    masterServerAddrSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    masterServerAddrSocket.bind(("192.168.1.14", 30003))
    while True:
        data, addr = masterServerAddrSocket.recvfrom(50000)
        try:
            incoming_data = json.loads(data)
            masterIP = incoming_data['address']
            break
        except:
            pass


def broadcastTx(tx):
    wait = 0
    while masterIP == "127.0.0.1":
        wait += 1
        time.sleep(1)
        if wait == 30:
            printLog("Utils", "Failed to send tx", "error")
            return False

    context = zmq.Context()
    #  Socket to talk to server
    print("Connecting to master server…")
    connSocket = context.socket(zmq.REQ)
    connSocket.connect("tcp://{}:30002".format(masterIP))

    txString = pickle.dumps(tx)

    printLog("Utils", "Sending tx to master server")
    connSocket.send(txString)

    #  Get the reply.
    message = connSocket.recv()
    connSocket.close()
    if "OK".encode() in message:
        printLog("Utils", "Tx submitted!")
    else:
        printLog("Utils", "Tx not submitted!", "error")


def getBalanceByOwner(address=None):
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


def checkVotingResult():
    questions = requests.get('http://{}:8000/master/voter/question'.format(masterIP))
    questions = questions.json()
    j = 1

    for question in questions:
        i = 0
        print("Question {} : {}".format(j, question['question']['question']))
        for ans in question['answers']:
            hashVal = hashlib.sha224(ans['answer'].encode()).hexdigest()
            print("{}. {} ({}) ได้คะแนน {} คะแนน".format(i + 1, ans['answer'], hashVal, getBalanceByOwner(hashVal)))
            i = i + 1
        j = j + 1

    j = 1


def createVotePower(amount):
    private_key_file = open("./keys/master/private.pem", "r")
    public_key_file = open("./keys/master/public.pem", "r")
    pk = private_key_file.read()
    pub = public_key_file.read()
    tx = Transaction()
    tx.setType("create")
    tx.setTxTo(address=pub, value=amount)
    tx.setTimestamp(time.time())
    tx.signSignature(privateKey=pk)
    tx.hashTx()
    broadcastTx(tx)


def transferToRegistration(regisNo, amount):
    private_key_file = open("./keys/master/private.pem", "r")
    public_key_file = open("./keys/master/public.pem", "r")
    regis_public_key_file = open("./keys/registration/{}/public.pem".format(regisNo), "r")
    pk = private_key_file.read()
    pub = public_key_file.read()
    regisPub = regis_public_key_file.read()
    tx = Transaction()
    tx.setType("transfer")
    tx.setTxFrom(address=pub, value=amount)
    tx.setTxTo(address=regisPub, value=amount)
    tx.setTimestamp(time.time())
    tx.signSignature(privateKey=pk)
    tx.hashTx()
    broadcastTx(tx)


def main():
    global chain
    masterAddressListener()
    clear()
    print("\n\n")
    print("Select function to execute")
    print(" 1. See voting result")
    print(" 2. Create vote power")
    print(" 3. Transfer vote power to registration computer")
    while True:
        try:
            selected = int(input(": "))
            break
        except ValueError:
            pass
    print("\n\n")
    if selected == 1:
        chain = Blockchain()
        checkVotingResult()
    elif selected == 2:
        while True:
            try:
                amount = int(input("Enter amount: "))
                break
            except ValueError:
                pass
        createVotePower(amount)
    elif selected == 3:
        while True:
            try:
                regisNo = int(input("Enter registration machine number: "))
                amount = int(input("Enter amount: "))
                break
            except ValueError:
                pass
        transferToRegistration(regisNo, amount)
    input("Press Enter to continue...")


if __name__ == "__main__":
    while True:
        main()

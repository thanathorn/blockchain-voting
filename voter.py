import json
import pickle
import socket
import time
import requests
import zmq

from helper import printLog
from transaction import Transaction

masterIP = "127.0.0.1"
clear = lambda: print('\n' * 100)
choose = []
questions = []


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


def createTx(pub, pk):
    global questions
    printLog("Voter", "Building transactions...")
    i = 0
    Txs = []
    for q in questions:
        selected = int(choose[i])
        address = q['answers'][selected-1]['address']
        tx = Transaction()
        tx.setType("transfer")
        tx.setTxFrom(address=pub, value=int(q['question']['vote_accepted']))
        tx.setTxTo(address=address, value=int(q['question']['vote_accepted']))
        tx.setTimestamp(time.time())
        tx.signSignature(privateKey=pk)
        tx.hashTx()
        Txs.append(tx)
        i = i + 1
    return Txs


def broadcastTx(tx):
    wait = 0
    while masterIP == "127.0.0.1":
        wait += 1
        time.sleep(1)
        if wait == 30:
            printLog("Voter", "Failed to submit answer(s)", "error")
            return False

    context = zmq.Context()
    #  Socket to talk to server
    print("Connecting to master server…")
    connSocket = context.socket(zmq.REQ)
    connSocket.connect("tcp://{}:30002".format(masterIP))

    txString = pickle.dumps(tx)

    printLog("Voter", "Sending answer to master server")
    connSocket.send(txString)

    #  Get the reply.
    message = connSocket.recv()
    connSocket.close()
    if "OK".encode() in message:
        printLog("Voter", "Answer submitted!")
    else:
        printLog("Voter", "Answer not submitted!", "error")


def main():
    global questions
    printLog("Voter", "Starting...")
    masterAddressListener()
    student_id = input("Enter your student ID: ")
    # Load Private key and Public key
    private_key_file = open("./keys/voter/{}/private.pem".format(student_id), "r")
    public_key_file = open("./keys/voter/{}/public.pem".format(student_id), "r")
    pk = private_key_file.read()
    pub = public_key_file.read()

    clear()

    questionNum = 1

    # Get questions
    questions = requests.get('http://127.0.0.1:8000/master/voter/question')
    questions = questions.json()

    # Print questions
    for question in questions:
        choiceNum = 0
        print("Question {} : {}".format(questionNum, question['question']['question']))
        for ans in question['answers']:
            print("{}. {}".format(choiceNum + 1, ans['answer']))
            choiceNum = choiceNum + 1
        questionNum = questionNum + 1
        while True:
            selectedChoice = input("Enter your choice:")
            try:
                selectedChoice = int(selectedChoice)
                if choiceNum >= selectedChoice > 0:
                    break
            except ValueError:
                pass

        choose.append(selectedChoice)
    printLog("Voter", "Submitting answer(s)...")
    Txs = createTx(pub, pk)
    for tx in Txs:
        broadcastTx(tx)
        time.sleep(1)
    print('Thanks for participation')
    time.sleep(5)
    clear()


if __name__ == "__main__":
    while True:
        main()

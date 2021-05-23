import socket
import time
import os
from transaction import Transaction

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(0.2)
server.bind(("", 30002))

clear = lambda: print('\n'*100)
choose = []

temp_var = [
    {
        "question": {
            "question_id": 1,
            "question": "Choose your prime minister",
            "vote_accepted": 1
        },
        "answers": [
            {
                "answer": "Too",
                "address": "asfkwnertvbmtjpbncxvbASFlmnLASHfnALSFjpo"
            }, {
                "answer": "Taksin",
                "address": "asfkwnertvbmtjpbncxvbASFlmnLASHfnALSFjpo"
            }
        ]
    },
    {
        "question": {
            "question_id": 2,
            "question": "Choose your grade",
            "vote_accepted": 1
        },
        "answers": [
            {
                "answer": "A",
                "address": "asfASFdbfgkwnertvbmtjpbncxvbASFlmnLASHfnALSFjpo"
            }, {
                "answer": "A+",
                "address": "asfkwAlmliOpnertvbmtjpbncxvbASFlmnLASHfnALSFjpo"
            }
        ]
    }
]

selected_answer = [
    {
        "question_id": "",
        "answer_address": ""
    },
    {
        "question_id": "",
        "answer_address": ""
    }
]


def getQuestion():
    pass


def createTx(pub,pk):
    i = 0
    tx = []
    for question in temp_var:
        select = choose[i]
        if(question == int (select)-1)
            address = question['answers']['address']
            tx2 = Transaction()
            tx2.setType("transfer")
            tx2.setTxFrom(address=pub, value="2000")
            tx2.setTxTo(address=address, value="2000")
            tx2.setTimestamp(16211767050)
            tx2.signSignature(privateKey=pk)
            tx2.hashTx()
            tx.append(tx2)
        i = i+1
    return tx


def vote():
    tx = createTx()
    broadcastTx(tx)


def broadcastTx(tx):
    server.sendto(tx, ('<broadcast>', 37020))
    print("message sent!")
    time.sleep(1)


pk = input("Enter your private key: ")
pub = input("Enter your public key: ")
clear()
j = 1

for question in temp_var:
    i = 0
    print("Question {} : {}".format(j,question['question']['question']))
    for ans in question['answers']:
        print ("{}. {}".format(i+1,ans['answer']))
        i = i+1
    j = j + 1
    choose.append(input("Enter your choice : "))
    clear()
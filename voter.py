import socket
import time
from transaction import Transaction

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(0.2)
server.bind(("", 30002))

pk = input("Enter your private key:")
pub = input("Enter your public key:")

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


def createTx():
    return Transaction("transfer")


def vote():
    tx = createTx()
    broadcastTx(tx)


def broadcastTx(tx):
    server.sendto(tx, ('<broadcast>', 37020))
    print("message sent!")
    time.sleep(1)



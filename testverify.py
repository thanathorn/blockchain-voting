from blockchain import Blockchain
from transaction import Transaction

chain = Blockchain()


def getTxByOwner(address=None):
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


print(getTxByOwner(""))

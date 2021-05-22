import hashlib, json
from collections import OrderedDict


class MerkleTree:
    def __init__(self, listoftransaction=None):
        self.listoftransaction = listoftransaction
        self.past_transaction = OrderedDict()

    def create_tree(self):
        listoftransaction = self.listoftransaction
        past_transaction = self.past_transaction
        temp_transaction = []

        for index in range(0, len(listoftransaction), 2):
            current = listoftransaction[index]
            if index + 1 != len(listoftransaction):
                current_right = listoftransaction[index + 1]
            else:
                current_right = ''
            current_hash = hashlib.sha256(current.encode('utf-8'))
            if current_right != '':
                current_right_hash = hashlib.sha256(current_right.encode('utf-8'))
            past_transaction[listoftransaction[index]] = current_hash.hexdigest()
            if current_right != '':
                past_transaction[listoftransaction[index + 1]] = current_right_hash.hexdigest()
            if current_right != '':
                temp_transaction.append(current_hash.hexdigest() + current_right_hash.hexdigest())
            else:
                temp_transaction.append(current_hash.hexdigest())
        if len(listoftransaction) != 1:
            self.listoftransaction = temp_transaction
            self.past_transaction = past_transaction
            self.create_tree()

    def Get_past_transacion(self):
        return self.past_transaction

    def Get_Root_leaf(self):
        last_key = list(self.past_transaction.keys())[-1]
        return self.past_transaction[last_key]
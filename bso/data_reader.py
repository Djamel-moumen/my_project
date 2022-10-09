from .classes import *

def read_data(filename: str) -> Transactions:
    with open(filename, "r") as f:
        content = f.read().splitlines()
    transactions = read_transactions(content)
    items = read_items(content)
    return Transactions(transactions, items)


def read_items(content: list) -> dict:
    assert content[0] == "LIST OF ITEMS" and "BEGIN_DATA" in content
    items = dict()
    for line in content[1:content.index("BEGIN_DATA")]:
        items[line.strip().split(" ")[0]] = line.strip().split(" ")[1]
    return items

def read_transactions(content: list) -> list:
    assert "BEGIN_DATA" in content and "END_DATA" in content
    transactions = list()
    for line in content[content.index("BEGIN_DATA") + 1:content.index("END_DATA")]:
        transactions.append(frozenset(line.strip().split(" ")))
    return transactions






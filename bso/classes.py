import random
from .utils import Tracker


class Transactions:
    def __init__(self, transactions: list, items: dict):
        self.__transactions = transactions
        self.__items = items
        self.__items_set = frozenset(self.__items.keys())

    @property
    def transactions(self):
        return self.__transactions.copy()

    @property
    def items_set(self):
        return self.__items_set

    @property
    def nbr_transactions(self):
        return len(self.__transactions)

    @property
    def nbr_items(self):
        return len(self.__items)

    @property
    def average_nbr_items_per_transaction(self):
        n = 0
        for transaction in self.__transactions:
            n += len(transaction)
        return n / self.nbr_transactions

    @property
    def density_index(self):
        return self.average_nbr_items_per_transaction / self.nbr_items

    def get_item_name(self, key):
        return self.__items[key]

    def get_random_ar(self, size):
        assert 2 <= size <= self.nbr_items
        antecedent = set(random.sample(self.items_set, size - 1))
        consequence = set(random.sample(self.items_set.difference(antecedent), 1))
        return AssociationRule(self, antecedent, consequence)

    def print_info(self):
        print(
            f"""Nbr transactions: {self.nbr_transactions}
Nbr items: {self.nbr_items}
Average Nbr items per transaction: {self.average_nbr_items_per_transaction}
Density index: {self.density_index}"""
        )


class AssociationRule:
    def __init__(self, transactions: Transactions, antecendent: set, consequence: set):
        assert antecendent.intersection(consequence) == set()
        self.__transactions = transactions
        self.__antecedent = frozenset(antecendent)
        self.__consequence = frozenset(consequence)
        self.__all_items = self.__antecedent.union(self.__consequence)
        self.__fitness = None
        self.__support = None
        self.__confiance = None
        self.__alpha = None
        self.__min_supp = None
        self.__min_conf = None

    @property
    def fitness(self):
        return self.__fitness

    @property
    def support(self):
        return self.__support

    @property
    def confiance(self):
        return self.__confiance

    @property
    def size(self):
        return len(self.__all_items)

    @property
    def antecedent(self):
        return self.__antecedent

    @property
    def consequence(self):
        return self.__consequence

    @Tracker.Track
    def get_fitness(
            self,
            alpha: float = 0.5,
            min_supp: float = 0.0,
            min_conf: float = 0.0) -> float:
        assert 0 <= alpha <= 1
        if self.__fitness_parameters_unchanged(alpha, min_supp, min_conf):
            return self.__fitness
        self.__update_fitness_parameters(alpha, min_supp, min_conf)
        self.__update_fitness(alpha, min_supp, min_conf)
        return self.__fitness

    def __update_fitness_parameters(
            self,
            alpha: float,
            min_supp: float,
            min_conf: float):
        self.__alpha = alpha
        self.__min_supp = min_supp
        self.__min_conf = min_conf

    def __fitness_parameters_unchanged(
            self,
            alpha: float,
            min_supp: float,
            min_conf: float):
        return self.__alpha == alpha and\
               self.__min_supp == min_supp and\
               self.__min_conf == min_conf

    @Tracker.Track
    def __update_fitness(
            self,
            alpha: float,
            min_supp: float,
            min_conf: float):
        assert 0 <= alpha <= 1

        nbr_transactions_containing_antecedent = 0
        nbr_transactions_containing_all_items = 0
        for transaction in self.__transactions.transactions:
            if self.__all_items.issubset(transaction):
                nbr_transactions_containing_all_items += 1
            if self.__antecedent.issubset(transaction):
                nbr_transactions_containing_antecedent += 1

        self.__support = nbr_transactions_containing_all_items / self.__transactions.nbr_transactions
        self.__confiance = nbr_transactions_containing_all_items / nbr_transactions_containing_antecedent \
            if nbr_transactions_containing_antecedent != 0 else 0
        self.__fitness = alpha * self.__support + (1 - alpha) * self.__confiance \
            if self.__support >= min_supp and self.__confiance >= min_conf else 0

    def get_neighbor(self, distance):
        antecedent = set(self.__antecedent)
        consequence = set(self.__consequence)
        for _ in range(distance):
            all_items = antecedent.union(consequence)
            if random.random() < 1/3:
                consequence = set(random.sample(self.__transactions.items_set.difference(all_items), 1))
            else:
                add_item = True if random.random() < 0.5 else False
                if len(all_items) == self.__transactions.nbr_items:
                    add_item = False
                elif len(all_items) == 2:
                    add_item = True
                if add_item:
                    item_to_add = random.sample(self.__transactions.items_set.difference(all_items), 1)
                    antecedent = antecedent.union(set(item_to_add))
                else:
                    item_to_remove = random.sample(antecedent, 1)
                    antecedent = antecedent.difference(set(item_to_remove))
        return AssociationRule(self.__transactions, antecedent, consequence)

    def get_neighbor_with_added_item(self):
        if self.size == self.__transactions.nbr_items:
            return self
        antecedent = set(self.__antecedent)
        item_to_add = random.sample(self.__transactions.items_set.difference(self.__all_items), 1)
        return AssociationRule(self.__transactions, antecedent.union(set(item_to_add)), self.consequence)

    def get_neighbor_with_removed_item(self):
        if self.size == 2:
            return self
        antecedent = set(self.__antecedent)
        item_to_remove = random.sample(antecedent, 1)
        return AssociationRule(self.__transactions, antecedent.difference(set(item_to_remove)), self.consequence)

    def get_neighbor_with_changed_consequence(self):
        new_consequence = set(random.sample(self.__transactions.items_set.difference(self.__all_items), 1))
        return AssociationRule(self.__transactions, self.antecedent, new_consequence)


    def __eq__(self, other):
        if not isinstance(other, AssociationRule):
            return False
        return self.antecedent == other.antecedent and self.consequence == other.consequence

    def __str__(self):
        antecedent_items = set([self.__transactions.get_item_name(item) for item in self.__antecedent])
        consequence_items = set([self.__transactions.get_item_name(item) for item in self.__consequence])
        return f"({','.join(antecedent_items)}) -> {'-'.join(consequence_items)} | fitness: {self.__fitness} | support: {self.__support} | confiance: {self.__confiance}"

    def to_dict(self):
        return {
            "antecedent": [self.__transactions.get_item_name(item) for item in self.__antecedent],
            "consequence": [self.__transactions.get_item_name(item) for item in self.__consequence],
            "support": round(self.__support, 6),
            "confiance": round(self.__confiance, 6),
            "fitness": round(self.__fitness, 6)
        }

    def __hash__(self):
        return hash(f"{self.__antecedent}{self.__consequence}")



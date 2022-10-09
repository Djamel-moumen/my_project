import random
from .classes import *


class Bee:
    def __init__(self):
        pass

    def search(self, starting_sol: AssociationRule, q_table, alpha, min_supp, min_conf, nbr_neighbors):
        current_sol = starting_sol
        best_sol = current_sol
        explored_sols = set()
        for i in range(nbr_neighbors):
            new_sol = current_sol.get_neighbor(1)
            explored_sols.add(new_sol)
            if new_sol.get_fitness(alpha, min_supp, min_conf) > current_sol.get_fitness(alpha, min_supp, min_conf):
                current_sol = new_sol
            if new_sol.get_fitness(alpha, min_supp, min_conf) > best_sol.get_fitness(alpha, min_supp, min_conf):
                best_sol = new_sol
        return best_sol, explored_sols


class Swarm:
    def __init__(self, nbr_bees, smart: bool, learning_rate, discount):
        self.__bees = [SmartBee() if smart else Bee() for _ in range(nbr_bees)]
        self.__q_table = QTable(learning_rate, discount) if smart else QTable()

    def search(self, ref_sol, alpha, min_supp, min_conf, nbr_neighbors):
        search_regions = self.__generate_search_regions(ref_sol)
        explored_sols = set()
        best_sol = ref_sol
        for bee in self.__bees:
            bee_best_sol, bee_explored_sols = bee.search(next(search_regions), self.__q_table, alpha, min_supp, min_conf, nbr_neighbors)
            explored_sols.update(bee_explored_sols)
            if bee_best_sol.get_fitness(alpha, min_supp, min_conf) > best_sol.get_fitness(alpha, min_supp, min_conf):
                best_sol = bee_best_sol
        return best_sol, explored_sols

    @property
    def nbr_bees(self):
        return len(self.__bees)

    @property
    def q_table(self):
        return self.__q_table

    def __generate_search_regions(self, ref_sol):
        for i in range(self.nbr_bees):
            yield ref_sol.get_neighbor(4)


class SmartBee:
    def __init__(self):
        self.__exploration_rate = 1

    def __get_new_sol(self, current_sol, action):
        if action == Action().add:
            return current_sol.get_neighbor_with_added_item()
        elif action == Action().remove:
            return current_sol.get_neighbor_with_removed_item()
        elif action == Action().change_consequence:
            return current_sol.get_neighbor_with_changed_consequence()
        else:
            raise Exception

    def search(self, starting_sol: AssociationRule, q_table, alpha, min_supp, min_conf, nbr_neighbors):
        current_sol = starting_sol
        best_sol = current_sol
        explored_sols = set()
        for i in range(nbr_neighbors):
            state = set(current_sol.consequence).pop()
            if random.random() < self.__exploration_rate:
                action = Action().get_random_action(no_remove=current_sol.size == 2)
                new_sol = self.__get_new_sol(current_sol, action)
            else:
                action = q_table.get_best_action(state, no_remove=current_sol.size == 2)
                new_sol = self.__get_new_sol(current_sol, action)
            r = new_sol.get_fitness(alpha, min_supp, min_conf) - current_sol.get_fitness(alpha, min_supp, min_conf)
            q_table.update(current_sol, new_sol, action, r)
            self.__exploration_rate *= 0.998
            explored_sols.add(new_sol)
            if new_sol.get_fitness(alpha, min_supp, min_conf) > current_sol.get_fitness(alpha, min_supp, min_conf):
                current_sol = new_sol
            if new_sol.get_fitness(alpha, min_supp, min_conf) > best_sol.get_fitness(alpha, min_supp, min_conf):
                best_sol = new_sol
        return best_sol, explored_sols

class Action:
    def __init__(self):
        self.__add = "add"
        self.__remove = "remove"
        self.__change_consequence = "chng"

    @property
    def add(self):
        return self.__add

    @property
    def remove(self):
        return self.__remove

    @property
    def change_consequence(self):
        return self.__change_consequence

    def get_random_action(self, no_remove):
        if no_remove:
            return random.choice([self.add, self.change_consequence])
        return random.choice([self.add, self.remove, self.change_consequence])


class QTable:
    def __init__(self, learning_rate=0.1, discount=0.9):
        assert 0 <= learning_rate <= 1 and 0 <= discount <= 1
        self.__table = dict()
        self.__learning_rate = learning_rate
        self.__discount = discount

    def get_best_action(self, state, no_remove):
        actions_values = self.__table.get(state, dict()).copy()
        if not actions_values:
            return Action().get_random_action(no_remove)
        if no_remove:
            actions_values.pop(Action().remove, None)
        return max(actions_values.items(), key=lambda x: x[1])[0]

    def get_best_value(self, state):
        actions_values = self.__table.get(state)
        if not actions_values:
            return 0
        return max(actions_values.items(), key=lambda x: x[1])[1]

    def update(self, current_sol, next_sol, action, r):
        state = set(current_sol.consequence).pop()
        next_state = set(next_sol.consequence).pop()
        state_dict = self.__table.get(state)
        if state_dict:
            state_dict[action] = (1 - self.__learning_rate) * state_dict[action] + \
                                 self.__learning_rate * (r + self.__discount * self.get_best_value(next_state))
        else:
            state_dict = {Action().add: 0, Action().remove: 0, Action().change_consequence: 0}
            state_dict[action] = (1 - self.__learning_rate) * state_dict[action] + \
                                 self.__learning_rate * (r + self.__discount * self.get_best_value(next_state))

            self.__table[state] = state_dict

    def __str__(self):
        return str(self.__table)

    def __len__(self):
        return len(self.__table)


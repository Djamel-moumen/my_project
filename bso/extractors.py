from .swarm import *
import time

class BSOExtractor:
    def __init__(self, nbr_bees, smart, learning_rate=0.1, discount=0.9, num=0):
        self.__swarm = Swarm(nbr_bees, smart, learning_rate, discount)
        self.__observers = set()
        self.__stopped = False
        self.__paused = False
        self.num = num

    def extract(self, transactions, alpha, min_supp, min_conf, max_chance, nbr_neighbors):
        chances_left = max_chance
        ref_sol = transactions.get_random_ar(6)
        sols = set()
        while not self.__stopped:
            best_sol, explored_sols = self.__swarm.search(ref_sol, alpha, min_supp, min_conf, nbr_neighbors)
            sols.update(explored_sols)
            while self.__paused:
                time.sleep(0.5)
            self.update(
                data={
                    "num": self.num,
                    "Nbr explored ars": len(sols),
                    "Explored sols": explored_sols,
                    "Average fitness": self.__calculate_mean(sols),
                    "best_sol": best_sol.to_dict()
                }
            )

            if best_sol.get_fitness(alpha, min_supp, min_conf) > ref_sol.get_fitness(alpha, min_supp, min_conf):
                ref_sol = best_sol
                chances_left = max_chance


    def __calculate_mean(self, sols):
        somme = 0
        for ar in list(sorted(list(sols), key=lambda x: x.fitness, reverse=True))[:100]:
            somme += ar.fitness
        return somme / 100

    def observe(self, observer):
        self.__observers.add(observer)

    def update(self, data):
        for observer in self.__observers:
            observer.update(data)

    def unobserve(self, observer):
        self.__observers.discard(observer)
        if len(self.__observers) == 0:
            self.__stopped = True

    def stop(self):
        self.__stopped = True

    def pause(self):
        self.__paused = True

    def resume(self):
        self.__paused = False

    @staticmethod
    def ars_list_to_dict(ars):
        return [ar.to_dict() for ar in ars]

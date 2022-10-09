from .data_reader import read_data
from . import extractors
import itertools
from .classes import AssociationRule
from .utils import Tracker
from matplotlib import pyplot as plt

folder = "Benchmarks"
category = "Sparse"
filename = "retail.txt"
root = f"{folder}/{category}/{filename}"
smart = False
text = "With RL" if smart else "No RL"
transactions = read_data(root)

strategies = [
    {
        "label": "1st combination",
        "nbr_bees": 40,
        "nbr_neighbors": 20,
        "max_chance": 4
    },
    {
        "label": "2nd combination",
        "nbr_bees": 20,
        "nbr_neighbors": 40,
        "max_chance": 4
    },
    {
        "label": "3rd combination",
        "nbr_bees": 40,
        "nbr_neighbors": 20,
        "max_chance": 8
    },
    {
        "label": "4th combination",
        "nbr_bees": 20,
        "nbr_neighbors": 40,
        "max_chance": 8
    }
]

strategies = [
    {
        "label": "1st combination",
        "nbr_bees": 40,
        "nbr_neighbors": 20,
        "max_chance": 1
    },
    {
        "label": "2nd combination",
        "nbr_bees": 20,
        "nbr_neighbors": 40,
        "max_chance": 1
    },
    {
        "label": "3rd combination",
        "nbr_bees": 40,
        "nbr_neighbors": 20,
        "max_chance": 5
    },
    {
        "label": "4th combination",
        "nbr_bees": 20,
        "nbr_neighbors": 40,
        "max_chance": 5
    },

    {
        "label": "5rd combination",
        "nbr_bees": 40,
        "nbr_neighbors": 20,
        "max_chance": 15
    },
    {
        "label": "6th combination",
        "nbr_bees": 20,
        "nbr_neighbors": 40,
        "max_chance": 15
    }
]

for strategy in strategies[:4]:
    extractor = extractors.BSOExtractor(nbr_bees=strategy["nbr_bees"], smart=smart)
    result, track_dict = extractor.extract(transactions, 1, 0, 0, max_chance=strategy["max_chance"], nbr_neighbors=strategy["nbr_neighbors"])
    plt.plot(track_dict.keys(), track_dict.values(), label=strategy["label"])



plt.xlabel('N° explored ars')
plt.ylabel('Top 100 ars average fitness')
plt.title(f'Fitness evolution ({filename[:-4]})')
plt.legend()
plt.grid()
plt.show()


print(Tracker.durations_dict)
print(Tracker.frequencies_dict)

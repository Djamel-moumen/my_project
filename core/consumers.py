import json
from channels.generic.websocket import WebsocketConsumer
from . import models
from bso.data_reader import read_data
from bso.extractors import BSOExtractor
import threading
import os

class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.extractors = list()
        self.mutex = threading.Semaphore()

        self.id = int(self.scope['url_route']['kwargs']['id'])

        obj = models.Document.objects.get(pk=self.id)
        self.send(
            text_data=json.dumps(
                {
                    "intent": "transaction_data",
                    "content": {
                        "Nbr transactions": obj.nbr_transactions,
                        "Nbr items": obj.nbr_items,
                        "Average Nbr items per transaction": round(obj.average_nbr_items_per_transaction, 2),
                        "Density index": round(obj.density_index, 6),
                    }
                }
            )
        )
        self.transactions = read_data(f"media/{obj.docfile.name}")

    def disconnect(self, code):
        for extractor in self.extractors:
            extractor.unobserve(self)
        """obj = models.Document.objects.get(id=self.id)
        if os.path.exists(f"media/{obj.docfile.name}"):
            os.remove(f"media/{obj.docfile.name}")
        obj.delete()"""

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        if text_data_json['intent'] == 'launch':
            self.launch(text_data_json['content'])
        elif text_data_json['intent'] == 'pause':
            self.pause()
        elif text_data_json['intent'] == 'stop':
            self.stop()
        elif text_data_json['intent'] == 'resume':
            self.resume()

    def launch(self, data):
        self.top_ars = set()
        for i, strat in enumerate(data):
            nbr_bees = int(strat['nbr_bees'])
            nbr_neighbors = int(strat['nbr_neighbors'])
            max_chance = int(strat['max_chance'])
            smart = strat['smart']
            alpha = (0.1 / self.transactions.density_index) / (0.1 / self.transactions.density_index + 1)
            extractor = BSOExtractor(nbr_bees=nbr_bees, smart=smart, num=i)
            self.extractors.append(extractor)
            extractor.observe(self)
            threading.Thread(target=extractor.extract, args=(self.transactions, alpha, 0, 0, max_chance, nbr_neighbors)).start()

        self.send(text_data=json.dumps({
            'intent': 'launch_started'
        }))


    def stop(self):
        for extractor in self.extractors:
            extractor.stop()
        self.extractors = list()
        self.send(text_data=json.dumps({
            'intent': 'launch_stopped'
        }))

    def pause(self):
        for extractor in self.extractors:
            extractor.pause()
        self.send(text_data=json.dumps({
            'intent': 'launch_paused'
        }))

    def resume(self):
        for extractor in self.extractors:
            extractor.resume()
        self.send(text_data=json.dumps({
            'intent': 'launch_resumed'
        }))

    def update(self, data):
        self.mutex.acquire()
        self.top_ars.update(data["Explored sols"])
        top_100 = list(sorted(list(self.top_ars), key=lambda x: x.fitness, reverse=True))[:100]
        self.top_ars = set(top_100)
        self.mutex.release()

        print(data["num"], data["Nbr explored ars"])

        self.send(text_data=json.dumps({
            'intent': 'update',
            'content': {
                "num": data["num"],
                "Nbr explored ars": data["Nbr explored ars"],
                "top 100 ars": MyConsumer.ars_list_to_dict(top_100),
                "Average fitness": data["Average fitness"],
                "best_sol": data["best_sol"]
            }
        }))

    @staticmethod
    def ars_list_to_dict(ars):
        return [ar.to_dict() for ar in ars]


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .maze import Maze, MazeEncoder

from random import randint


class MazeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'maze': Maze(10, 10, randint(0, 9), randint(0, 9))
        }, cls=MazeEncoder))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        print(text_data)

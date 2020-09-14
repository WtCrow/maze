from channels.generic.websocket import AsyncWebsocketConsumer
from .maze import Maze, MazeEncoder
from random import randint
import asyncio
import json


class MazeConsumer(AsyncWebsocketConsumer):
    START_STATUS = 'start'
    RECEIVE_STATUS = 'receive'
    WAIT_NAME_STATUS = 'wait_name'

    TIMER_EVENT = 'time'
    NEW_MAZE_EVENT = 'new_maze'
    NEW_COORD_EVENT = 'new_coord'
    GAME_OVER_EVENT = 'game_over'
    ERROR_EVENT = 'error'

    time_on_cell = .15

    async def connect(self):
        self.game_status = MazeConsumer.START_STATUS
        self.score = 0
        self.maze_size = 10
        self.time_left = self.maze_size * self.maze_size * MazeConsumer.time_on_cell

        await self.accept()

        asyncio.get_event_loop().create_task(self.timer())
        await self.send_new_maze()
        self.status = MazeConsumer.RECEIVE_STATUS

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        print(text_data)

    async def timer(self):
        while True:
            await self.send(text_data=json.dumps({'event': MazeConsumer.TIMER_EVENT, 'time': self.time_left}))
            await asyncio.sleep(1)
            self.time_left -= 1

            if self.time_left == -1:
                self.game_status = MazeConsumer.WAIT_NAME_STATUS
                await self.send(text_data=json.dumps({'event': MazeConsumer.GAME_OVER_EVENT}))
                break

    async def send_new_maze(self):
        self.maze = Maze(self.maze_size, self.maze_size, randint(0, self.maze_size - 1), randint(0, self.maze_size - 1))
        await self.send(text_data=json.dumps({
            'event': MazeConsumer.NEW_MAZE_EVENT,
            'maze': self.maze,
            'score': self.score,
        }, cls=MazeEncoder))

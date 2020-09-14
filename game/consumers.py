from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ScoreRecord
from .maze import Maze, MazeEncoder
from random import randint
import asyncio
import json


class MazeConsumer(AsyncWebsocketConsumer):
    START_STATUS = 'start'
    WAIT_MOVE_STATUS = 'wait_move'
    WAIT_NAME_STATUS = 'wait_name'

    # server events
    TIMER_EVENT = 'time'
    NEW_MAZE_EVENT = 'new_maze'
    NEW_COORD_EVENT = 'new_coord'
    GAME_OVER_EVENT = 'game_over'
    ERROR_EVENT = 'error'

    # client events
    MOVE_EVENT = 'move'
    NAME_EVENT = 'name'

    time_on_cell = .1

    async def connect(self):
        self.game_status = MazeConsumer.START_STATUS
        self.score = 0
        self.maze_size = 10
        self.time_left = 0

        await self.accept()

        asyncio.get_event_loop().create_task(self.timer())
        await self.send_new_maze()
        self.game_status = MazeConsumer.WAIT_MOVE_STATUS

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # TODO: create DRF serializer and move validation there
        try:
            client_message = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'event': MazeConsumer.ERROR_EVENT,
                'data': 'Bad message format.',
            }))
            return

        if 'event' not in client_message:
            await self.send(text_data=json.dumps({
                'event': MazeConsumer.ERROR_EVENT,
                'data': 'Message not contain "event" key.',
            }))
            return

        if client_message['event'] == MazeConsumer.MOVE_EVENT:
            if self.game_status != MazeConsumer.WAIT_MOVE_STATUS:
                await self.send(text_data=json.dumps({
                    'event': MazeConsumer.ERROR_EVENT,
                    'data': 'Server not receive message for move.',
                }))
                return

            if client_message.get('data') not in (Maze.RIGHT, Maze.LEFT, Maze.TOP, Maze.BOTTOM):
                await self.send(text_data=json.dumps({
                    'event': MazeConsumer.ERROR_EVENT,
                    'message': f'Bad "data" key '
                               f'(must: "{Maze.RIGHT}" | "{Maze.LEFT}" | "{Maze.TOP}" | "{Maze.BOTTOM}").',
                }))
                return

            self.maze.go_to(client_message['data'])
            if self.maze.is_finish():
                self.score += 1
                self.maze_size += 5
                await self.send_new_maze()
            else:
                await self.send(text_data=json.dumps({
                    'event': MazeConsumer.NEW_COORD_EVENT,
                    'data': (self.maze.x, self.maze.y),
                }))
        elif client_message['event'] == MazeConsumer.NAME_EVENT:
            if self.game_status != MazeConsumer.WAIT_NAME_STATUS:
                await self.send(text_data=json.dumps({
                    'event': MazeConsumer.ERROR_EVENT,
                    'data': 'Server not receive message for set name.',
                }))
                return
            name = str(client_message.get('data', ''))
            if not name or len(name) > 20:
                await self.send(text_data=json.dumps({
                    'event': MazeConsumer.ERROR_EVENT,
                    'data': 'Bad name format (0 < length <= 20).',
                }))
                return

            await self.write_to_table(name)
            await self.close(code=1000)

    @database_sync_to_async
    def write_to_table(self, name):
        ScoreRecord.objects.create(name=name, score=self.score)

    async def timer(self):
        while True:
            await self.send(text_data=json.dumps({'event': MazeConsumer.TIMER_EVENT, 'data': self.time_left}))
            await asyncio.sleep(1)
            self.time_left -= 1

            if self.time_left == 0:
                self.game_status = MazeConsumer.WAIT_NAME_STATUS
                await self.send(text_data=json.dumps({'event': MazeConsumer.TIMER_EVENT, 'data': self.time_left}))
                await self.send(text_data=json.dumps({'event': MazeConsumer.GAME_OVER_EVENT}))
                break

    async def send_new_maze(self):
        self.maze = Maze(self.maze_size, self.maze_size, randint(0, self.maze_size - 1), randint(0, self.maze_size - 1))
        self.time_left += int(self.maze_size * self.maze_size * MazeConsumer.time_on_cell)
        await self.send(text_data=json.dumps({
            'event': MazeConsumer.NEW_MAZE_EVENT,
            'data': {'maze': self.maze, 'score': self.score, 'time': self.time_left}
        }, cls=MazeEncoder))

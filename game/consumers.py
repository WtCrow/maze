from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .maze import Maze, MazeEncoder
from .models import ScoreRecord
from random import randint
import asyncio
import json


class MazeConsumer(AsyncWebsocketConsumer):
    """Consumer maze-game messages

    On connect will send start maze and status_game changed from start on wait_move
    In background worked timer task and send to client message with current time in format:
    {
        event: time,
        content: time -> int  # current time left
    }
    If time == 0, status changed on wait_name and send to client message:
    {
        event: game_over,
        content: user_score -> int  # final user score
    }

    status == start
        status set while first maze not sent
        server not received messages
    status == wait_move
        server receive messages in format:
        {
            event: move,
            content: direction -> str from list('r', 'l', 't', 'b')  # this direction for movement in maze
                                                                     # r - right, l - left, t - top, b - bottom
        }
        if user moved on finish, will send new maze and time will be increased,
        else server send new coordinate in maze
        {
            event: new_coord,
            content: [x, y] -> (int, int)
        }
    status == wait_name
        server receive messages in format:
        {
            event: name,
            content: name -> str(min_len=0, max_len=20)
        }
        score and name will be save in DB and connection will be close

    If send invalid data, server send message in format
    {
        event: error,
        content: message -> str
    }

    new_maze event message
    {
        event: new_maze,
        content: {maze: maze, -> str  # json_dumps Maze object, view maze.py
                  score: score, -> int  # current user score
                  time: time_left -> int # current time left
                 }
    }

    """
    # server statuses for current connect
    START_STATUS = 'start'
    WAIT_MOVE_STATUS = 'wait_move'
    WAIT_NAME_STATUS = 'wait_name'

    # server side events
    TIMER_EVENT = 'time'
    NEW_MAZE_EVENT = 'new_maze'
    NEW_COORD_EVENT = 'new_coord'
    GAME_OVER_EVENT = 'game_over'
    ERROR_EVENT = 'error'

    # client side events
    MOVE_EVENT = 'move'
    NAME_EVENT = 'name'

    # modifier for time_on_cell. Used on each new level.
    MOD_TIME = .85

    async def connect(self):
        self.time_on_cell = .1
        self.score = 0
        self.maze_size = 10
        self.time_left = 0

        await self.accept()

        await self.send_new_maze()
        self.timer_task = asyncio.get_event_loop().create_task(self.timer())
        self.game_status = MazeConsumer.WAIT_MOVE_STATUS

    async def disconnect(self, close_code):
        self.timer_task.cancel()

    async def receive(self, text_data):
        from .serializers import MazeMessageSerializer

        try:
            client_message = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error('Bad message format.')
            return
        serializer = MazeMessageSerializer(data=client_message, context={'status': self.game_status})
        if not serializer.is_valid():
            error = str(list(serializer.errors.values())[0][0])
            await self.send_error(error)
            return

        if client_message['event'] == MazeConsumer.MOVE_EVENT:
            self.maze.go_to(client_message['content'])
            if self.maze.is_finish():
                self.score += 1
                if self.maze_size < 50:
                    self.maze_size += 5
                self.time_on_cell *= MazeConsumer.MOD_TIME
                await self.send_new_maze()
            else:
                await self.send(text_data=json.dumps({
                    'event': MazeConsumer.NEW_COORD_EVENT,
                    'content': (self.maze.x, self.maze.y),
                }))
        elif client_message['event'] == MazeConsumer.NAME_EVENT:
            name = str(client_message.get('content', ''))

            await self.write_to_table(name)
            await self.close(code=1000)

    @database_sync_to_async
    def write_to_table(self, name):
        ScoreRecord.objects.create(name=name, score=self.score)

    async def timer(self):
        try:
            while True:
                await self.send(text_data=json.dumps({'event': MazeConsumer.TIMER_EVENT, 'content': self.time_left}))
                await asyncio.sleep(1)
                self.time_left -= 1

                if self.time_left == 0:
                    self.game_status = MazeConsumer.WAIT_NAME_STATUS
                    await self.send(text_data=json.dumps({'event': MazeConsumer.TIMER_EVENT, 'content': self.time_left}))
                    await self.send(text_data=json.dumps({'event': MazeConsumer.GAME_OVER_EVENT, 'content': self.score}))
                    break
        except asyncio.CancelledError:
            pass

    async def send_new_maze(self):
        self.maze = Maze(self.maze_size, self.maze_size, randint(0, self.maze_size - 1), randint(0, self.maze_size - 1))
        self.time_left += int(self.maze_size * self.maze_size * self.time_on_cell)
        await self.send(text_data=json.dumps({
            'event': MazeConsumer.NEW_MAZE_EVENT,
            'content': {'maze': self.maze, 'score': self.score, 'time': self.time_left}
        }, cls=MazeEncoder))

    async def send_error(self, error):
        await self.send(text_data=json.dumps({
            'event': MazeConsumer.ERROR_EVENT,
            'content': error,
        }))

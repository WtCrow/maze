from channels.testing import ChannelsLiveServerTestCase
from selenium.webdriver.firefox.options import Options
from django.test import LiveServerTestCase
from game.consumers import MazeConsumer
from maze.settings import BASE_DIR
from aiohttp import ClientSession
from django.urls import reverse
from selenium import webdriver
from random import randint
from game.maze import Maze
from unittest import skip
from game.models import *
import asyncio
import json
import re

TABLE_URL_NAME = 'table'
GAME_WS_URL = 'api/v1/ws/maze'


class TestTablePage(LiveServerTestCase):
    """Test page with top 10 rating table"""
    headless = True

    def go_to_page(self, name_url, **kwargs):
        """Selenium go to page by url name"""
        url = reverse(name_url, kwargs=kwargs)
        self.selenium.get('%s%s' % (self.live_server_url, url))

    @classmethod
    def setUpClass(cls):
        super(TestTablePage, cls).setUpClass()
        options = Options()
        options.headless = cls.headless
        cls.selenium = webdriver.Firefox(options=options, executable_path=f'{BASE_DIR}/geckodriver')
        cls.selenium.implicitly_wait(1)

    @classmethod
    def setUp(cls):
        max_score = 10

        cls.users_records = dict()
        for i in range(0, 10):
            name = f'test_{i}'
            score = randint(1, max_score)
            cls.users_records[name] = score
            ScoreRecord.objects.create(name=name, score=score)

        # user, that not display in table
        cls.worst_user = 'test_11'
        cls.users_records[cls.worst_user] = 0

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TestTablePage, cls).tearDownClass()

    def test_table_page_contain_sorted_scores_rows(self):
        self.go_to_page(TABLE_URL_NAME)
        rows = self.selenium.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        scores = [int(row.find_elements_by_tag_name('td')[1].text) for row in rows]

        self.assertTrue(all(a >= b for a, b in zip(scores, scores[1:])), msg='Score table not sorted')

    def test_all_rows_display_correct_pairs(self):
        """All pairs (name, score) in tables match with pairs in data base"""
        self.go_to_page(TABLE_URL_NAME)
        rows = self.selenium.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        records = [(re.match('\d+. ([^\n]*)', row.find_elements_by_tag_name('td')[0].text)[1],
                    int(row.find_elements_by_tag_name('td')[1].text))
                   for row in rows]

        self.assertTrue(all(self.users_records[name] == score for name, score in records),
                        msg='Table pairs does not match with pairs in data base')

    def test_display_only_best_ten_results(self):
        """Worst user not in table"""
        self.go_to_page(TABLE_URL_NAME)
        rows = self.selenium.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        records = [(re.match('\d+. ([^\n]*)', row.find_elements_by_tag_name('td')[0].text)[1],
                    int(row.find_elements_by_tag_name('td')[1].text))
                   for row in rows]

        self.assertNotIn((self.worst_user, self.users_records[self.worst_user]), records, 'Worst user in table')


class TestMaze(ChannelsLiveServerTestCase):

    async def _test_movement(self):
        async with ClientSession() as session:
            ws_url = f'{self.live_server_url}/{GAME_WS_URL}'
            async with session.ws_connect(ws_url) as ws:
                response = await ws.receive()
                data = json.loads(response.data)
                self.assertEqual(data['event'], MazeConsumer.NEW_MAZE_EVENT, msg='First event not new maze')

                # create maze on data from response
                maze = Maze(is_generate=False)
                maze.matrix_walls = data['content']['maze']['matrix']
                maze.x = data['content']['maze']['current_x']
                maze.y = data['content']['maze']['current_y']
                maze.max_depth_x = data['content']['maze']['current_x']
                maze.max_depth_y = data['content']['maze']['max_depth_y']

                # go to some free path direction
                free_path = maze.get_access_paths()[0]
                await ws.send_json({'event': MazeConsumer.MOVE_EVENT, 'content': free_path})
                maze.go_to(free_path)

                while True:
                    # possible events: TIMER_EVENT and NEW_COORD_EVENT
                    response = await ws.receive()
                    data = json.loads(response.data)

                    if data['event'] == MazeConsumer.TIMER_EVENT:
                        continue
                    elif data['event'] == MazeConsumer.NEW_COORD_EVENT:
                        self.assertEqual((maze.x, maze.y), (data['content'][0], data['content'][1]),
                                         msg='Bad coordinates')
                        break
                    else:
                        self.assertTrue(False, msg='Unexpected event')

    async def _test_timer(self):
        async with ClientSession() as session:
            ws_url = f'{self.live_server_url}/{GAME_WS_URL}'
            async with session.ws_connect(ws_url) as ws:
                time = None
                next_time = None
                while True:
                    response = await ws.receive()
                    data = json.loads(response.data)
                    if data['event'] == MazeConsumer.TIMER_EVENT:
                        if not time or not next_time:
                            time = data['content']
                            next_time = time - 1  # next time value should be less on 1
                        else:
                            self.assertEqual(data['content'], next_time, msg='Unexpected time value')
                            time = data['content']
                            next_time -= 1  # next time value should be less on 1
                    elif data['event'] == MazeConsumer.GAME_OVER_EVENT:
                        self.assertEqual(time, 0, msg='Sent game over event, but time != 0')
                        break

    def test_movement(self):
        """Test movements in some free path direction"""
        asyncio.get_event_loop().run_until_complete(self._test_movement())

    def test_timer(self):
        """Timer decrement on 1 each step, if timer == 0, send game over event"""
        asyncio.get_event_loop().run_until_complete(self._test_timer())

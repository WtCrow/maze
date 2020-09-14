from json import JSONEncoder, JSONDecoder
from random import choice, randint
from copy import copy


class Maze:
    RIGHT = 'r'
    LEFT = 'l'
    TOP = 't'
    BOTTOM = 'b'
    
    def __init__(self, rows_count, columns_count, start_x=0, start_y=0):
        self.x = start_x
        self.y = start_y

        cell_pattern = {Maze.RIGHT: True, Maze.LEFT: True,
                        Maze.TOP: True, Maze.BOTTOM: True,
                        'is_init': False}
        self.matrix_walls = [[copy(cell_pattern) for x in range(columns_count)] for y in range(rows_count)]

        self.max_depth, self.curr_depth = 0, 0
        self.max_depth_x, self.max_depth_y = 0, 0

        self.go_to_cell(self.x, self.y)

    def get_access_ways(self):
        access_ways = []
        if not self.matrix_walls[self.y][self.x][Maze.RIGHT]:
            access_ways.append(Maze.RIGHT)
        if not self.matrix_walls[self.y][self.x][Maze.LEFT]:
            access_ways.append(Maze.LEFT)
        if not self.matrix_walls[self.y][self.x][Maze.TOP]:
            access_ways.append(Maze.TOP)
        if not self.matrix_walls[self.y][self.x][Maze.BOTTOM]:
            access_ways.append(Maze.BOTTOM)
        return access_ways

    def go_to(self, way):
        access_ways = self.get_access_ways()
        if way not in access_ways:
            return self.x, self.y

        while True:
            if way == Maze.RIGHT:
                self.x += 1
                access_ways = self.get_access_ways()
                access_ways.remove(Maze.LEFT)
            elif way == Maze.LEFT:
                self.x -= 1
                access_ways = self.get_access_ways()
                access_ways.remove(Maze.RIGHT)
            elif way == Maze.TOP:
                self.y -= 1
                access_ways = self.get_access_ways()
                access_ways.remove(Maze.BOTTOM)
            elif way == Maze.BOTTOM:
                self.y += 1
                access_ways = self.get_access_ways()
                access_ways.remove(Maze.TOP)
            if len(access_ways) != 1:
                break
            way = access_ways[0]
        return self.x, self.y

    def is_finish(self):
        return self.x == self.max_depth_x and self.y == self.max_depth_y

    def _get_not_inited_ways(self, x, y):
        not_inited = []
        if x < len(self.matrix_walls[0]) - 1 and not self.matrix_walls[y][x + 1]['is_init']:
            not_inited.append(Maze.RIGHT)
        if x > 0 and not self.matrix_walls[y][x - 1]['is_init']:
            not_inited.append(Maze.LEFT)
        if y > 0 and not self.matrix_walls[y - 1][x]['is_init']:
            not_inited.append(Maze.TOP)
        if y < len(self.matrix_walls) - 1 and not self.matrix_walls[y + 1][x]['is_init']:
            not_inited.append(Maze.BOTTOM)
        return not_inited

    def go_to_cell(self, x, y):
        self.matrix_walls[y][x]['is_init'] = True

        self.curr_depth += 1
        if self.curr_depth > self.max_depth:
            self.max_depth = self.curr_depth
            self.max_depth_x = x
            self.max_depth_y = y
        not_inited = self._get_not_inited_ways(x, y)

        while not_inited:
            way = choice(not_inited)
            not_inited.remove(way)
            if way == Maze.RIGHT:
                self.matrix_walls[y][x][Maze.RIGHT] = False
                self.matrix_walls[y][x + 1][Maze.LEFT] = False
                self.go_to_cell(x + 1, y)
            elif way == Maze.LEFT:
                self.matrix_walls[y][x][Maze.LEFT] = False
                self.matrix_walls[y][x - 1][Maze.RIGHT] = False
                self.go_to_cell(x - 1, y)
            elif way == Maze.TOP:
                self.matrix_walls[y][x][Maze.TOP] = False
                self.matrix_walls[y - 1][x][Maze.BOTTOM] = False
                self.go_to_cell(x, y - 1)
            elif way == Maze.BOTTOM:
                self.matrix_walls[y][x][Maze.BOTTOM] = False
                self.matrix_walls[y + 1][x][Maze.TOP] = False
                self.go_to_cell(x, y + 1)
            self.curr_depth -= 1
            not_inited = self._get_not_inited_ways(x, y)


class MazeEncoder(JSONEncoder):
    def default(self, maze):

        matrix = [[{Maze.RIGHT: cell[Maze.RIGHT], Maze.LEFT: cell[Maze.LEFT],
                    Maze.TOP: cell[Maze.TOP], Maze.BOTTOM: cell[Maze.BOTTOM]}
                   for cell in row] for row in maze.matrix_walls]

        return {'matrix': matrix,
                'current_x': maze.x, 'current_y': maze.y,
                'max_depth_x': maze.max_depth_x, 'max_depth_y': maze.max_depth_y}


if __name__ == '__main__':
    import sys
    import json

    sys.setrecursionlimit(10000)
    m = Maze(100, 100, randint(0, 99), randint(0, 99))
    m_json = json.dumps(m, cls=MazeEncoder)
    print(m_json)

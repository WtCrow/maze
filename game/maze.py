from json import JSONEncoder, JSONDecoder
from random import choice, randint
from copy import copy


class Maze:
    RIGHT_WALL = 'r'
    LEFT_WALL = 'l'
    TOP_WALL = 't'
    BOTTOM_WALL = 'b'
    
    def __init__(self, rows_count, columns_count, start_x=0, start_y=0, is_generate=True):
        self.rows_count = rows_count
        self.columns_count = columns_count
        self.start_x = start_x
        self.start_y = start_y

        cell_pattern = {Maze.RIGHT_WALL: True, Maze.LEFT_WALL: True,
                        Maze.TOP_WALL: True, Maze.BOTTOM_WALL: True,
                        'is_init': False}
        self.matrix = [[copy(cell_pattern) for x in range(columns_count)] for y in range(rows_count)]

        self.max_depth = 0
        self.curr_depth = 0
        self.x_max_depth, self.y_max_depth = 0, 0

        if is_generate:
            self.go_to_cell(start_x, start_y)

    def get_not_inited_ways(self, x, y):
        access_ways = []
        if x < self.columns_count - 1 and not self.matrix[y][x + 1]['is_init']:
            access_ways.append(Maze.RIGHT_WALL)
        if x > 0 and not self.matrix[y][x - 1]['is_init']:
            access_ways.append(Maze.LEFT_WALL)
        if y > 0 and not self.matrix[y - 1][x]['is_init']:
            access_ways.append(Maze.TOP_WALL)
        if y < self.rows_count - 1 and not self.matrix[y + 1][x]['is_init']:
            access_ways.append(Maze.BOTTOM_WALL)
        return access_ways

    def go_to_cell(self, x, y):
        self.matrix[y][x]['is_init'] = True

        self.curr_depth += 1
        if self.curr_depth > self.max_depth:
            self.max_depth = self.curr_depth
            self.x_max_depth = x
            self.y_max_depth = y
        access_ways = self.get_not_inited_ways(x, y)

        while access_ways:
            way = choice(access_ways)
            access_ways.remove(way)
            if way == Maze.RIGHT_WALL:
                self.matrix[y][x][Maze.RIGHT_WALL] = False
                self.matrix[y][x + 1][Maze.LEFT_WALL] = False
                self.go_to_cell(x + 1, y)
            elif way == Maze.LEFT_WALL:
                self.matrix[y][x][Maze.LEFT_WALL] = False
                self.matrix[y][x - 1][Maze.RIGHT_WALL] = False
                self.go_to_cell(x - 1, y)
            elif way == Maze.TOP_WALL:
                self.matrix[y][x][Maze.TOP_WALL] = False
                self.matrix[y - 1][x][Maze.BOTTOM_WALL] = False
                self.go_to_cell(x, y - 1)
            elif way == Maze.BOTTOM_WALL:
                self.matrix[y][x][Maze.BOTTOM_WALL] = False
                self.matrix[y + 1][x][Maze.TOP_WALL] = False
                self.go_to_cell(x, y + 1)
            self.curr_depth -= 1
            access_ways = self.get_not_inited_ways(x, y)


class MazeEncoder(JSONEncoder):
    def default(self, maze):

        matrix = [[{Maze.RIGHT_WALL: cell[Maze.RIGHT_WALL], Maze.LEFT_WALL: cell[Maze.LEFT_WALL],
                    Maze.TOP_WALL: cell[Maze.TOP_WALL], Maze.BOTTOM_WALL: cell[Maze.BOTTOM_WALL]}
                   for cell in row] for row in maze.matrix]

        return {'matrix': matrix,
                'x_start': maze.start_x, 'y_start': maze.start_y,
                'x_max_depth': maze.x_max_depth, 'y_max_depth': maze.y_max_depth}


if __name__ == '__main__':
    import sys
    import json

    sys.setrecursionlimit(10000)
    m = Maze(100, 100, randint(0, 99), randint(0, 99))
    m_json = json.dumps(m, cls=MazeEncoder)
    print(m_json)

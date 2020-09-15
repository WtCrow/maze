from random import choice, randint
from json import JSONEncoder
from copy import copy


class Maze:
    """Class with recursive-generated maze and user, finish coordinates"""

    # access paths direction
    RIGHT = 'r'
    LEFT = 'l'
    TOP = 't'
    BOTTOM = 'b'
    
    def __init__(self, rows_count, columns_count, start_x=0, start_y=0):
        self.x = start_x
        self.y = start_y

        # not inited cell with all walls
        cell_pattern = {Maze.RIGHT: True, Maze.LEFT: True,
                        Maze.TOP: True, Maze.BOTTOM: True,
                        'is_init': False}
        self.matrix_walls = [[copy(cell_pattern) for x in range(columns_count)] for y in range(rows_count)]

        # finish coordinates
        self.max_depth, self.curr_depth = 0, 0
        self.max_depth_x, self.max_depth_y = 0, 0

        # start generate
        self.init_cell(self.x, self.y)

    def get_access_paths(self):
        """get path cell without wall"""
        return list(filter(lambda path: not self.matrix_walls[self.y][self.x][path],
                           (Maze.RIGHT, Maze.LEFT, Maze.TOP, Maze.BOTTOM)))

    def go_to(self, path):
        """Move while exist only one path except cell from where come

        Return new coordinates

        """

        access_paths = self.get_access_paths()
        if path not in access_paths:
            return self.x, self.y

        while True:
            if path == Maze.RIGHT:
                self.x += 1
                access_paths = self.get_access_paths()
                access_paths.remove(Maze.LEFT)
            elif path == Maze.LEFT:
                self.x -= 1
                access_paths = self.get_access_paths()
                access_paths.remove(Maze.RIGHT)
            elif path == Maze.TOP:
                self.y -= 1
                access_paths = self.get_access_paths()
                access_paths.remove(Maze.BOTTOM)
            elif path == Maze.BOTTOM:
                self.y += 1
                access_paths = self.get_access_paths()
                access_paths.remove(Maze.TOP)
            if len(access_paths) != 1:
                break
            path = access_paths[0]
        return self.x, self.y

    def is_finish(self):
        """Check: finish == current position"""
        return self.x == self.max_depth_x and self.y == self.max_depth_y

    def _get_not_inited_paths(self, x, y):
        """Get neighboring not inited cells by x and y"""
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

    def init_cell(self, x, y):
        """Start recursive maze generate.

        Go to random not inited neighboring cell
        If not neighboring not inited cell then return

        """
        self.matrix_walls[y][x]['is_init'] = True

        # calculate max depth
        self.curr_depth += 1
        if self.curr_depth > self.max_depth:
            self.max_depth = self.curr_depth
            self.max_depth_x = x
            self.max_depth_y = y
        not_inited = self._get_not_inited_paths(x, y)

        # get all neighboring not inited cell except cell from where come
        while not_inited:
            path = choice(not_inited)
            not_inited.remove(path)
            if path == Maze.RIGHT:
                # crush wall by path and crush wall neighboring cell by inverse path
                self.matrix_walls[y][x][Maze.RIGHT] = False
                self.matrix_walls[y][x + 1][Maze.LEFT] = False
                self.init_cell(x + 1, y)
            elif path == Maze.LEFT:
                self.matrix_walls[y][x][Maze.LEFT] = False
                self.matrix_walls[y][x - 1][Maze.RIGHT] = False
                self.init_cell(x - 1, y)
            elif path == Maze.TOP:
                self.matrix_walls[y][x][Maze.TOP] = False
                self.matrix_walls[y - 1][x][Maze.BOTTOM] = False
                self.init_cell(x, y - 1)
            elif path == Maze.BOTTOM:
                self.matrix_walls[y][x][Maze.BOTTOM] = False
                self.matrix_walls[y + 1][x][Maze.TOP] = False
                self.init_cell(x, y + 1)
            self.curr_depth -= 1
            not_inited = self._get_not_inited_paths(x, y)


class MazeEncoder(JSONEncoder):
    """JSON encoder for Maze object

    Contain:
        matrix: [[cell, cell],[],[]...]. cell format: {r: bool, l: bool, t: bool, b: bool}
        current_x, current_y - start user coord
        max_depth_x, max_depth_y - finish

    """

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

import pygame
from sys import exit
from random import choice
from time import time


class TetrisGame:
    BG_COLOR = (127, 127, 127)
    COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 100, 10), (255, 255, 0), (240, 0, 255), (115, 0, 0),
              (230, 220, 170), (255, 255, 255), (153, 0, 153), (255, 100, 100), (200, 0, 0), (0, 0, 128)]
    SHAPES = ['I', 'J', 'L', 'O', 'Z', 'T', 'S']
    DELLAY = 0.15

    def __init__(self):
        # GETTING CURRENT SCREEN RESOLUTION
        pygame.display.init()

        self.screen_height = pygame.display.Info().current_h - int(pygame.display.Info().current_h * 0.1)
        self.screen_height -= self.screen_height % 20
        self.screen_width = (self.screen_height // 20) * 10

        # CREATING PIECES CHARACTERISTICS
        self.shape_width = self.screen_height // 20

        # CREATING SCREEN
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # GAME VARIABLES
        self.begin = True
        self.current = []
        self.next = []
        self.__pick_rand()
        self.shape = Shape(self.screen, self.shape_width, self.current[0], self.current[1])
        self.shape.create()
        self.board = [[0 for j in range(10)] for i in range(20)]
        self.history_shapes = []
        self.history_colors = []
        self.counter = [0 for _ in range(20)]
        self.time = 0
        self.dellay = self.DELLAY

    def run_game(self):
        clock = pygame.time.Clock()
        while True:
            self.time += clock.get_rawtime()
            clock.tick()
            self.__check_events()
            if self.time / 1000 > self.dellay:
                self.shape.move_down()
                self.time = 0
            self.__check_collision()
            self.__update()

    def __check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                self.__check_keydown_events(event)
            # RETURNS TRUE IF A KEY DOWN HAS OCCURRED (for the collision method in order to know if a key was pressed)
                return True

    def __check_keydown_events(self, event):
        if event.key == pygame.K_UP:
            self.time = -100
            self.shape.rotate(self.board)

        elif event.key == pygame.K_RIGHT:
            self.time = -100
            self.shape.move_right(self.board)

        elif event.key == pygame.K_LEFT:
            self.time = -100
            self.shape.move_left(self.board)
        elif event.key == pygame.K_DOWN:
            # MAKES THE dellay 0 IN ORDER TO MAKE IT MOVE VERY FAST
            self.dellay = 0

    def __pick_rand(self):
        if self.begin:
            self.current.append(choice(self.SHAPES))
            self.current.append(choice(self.COLORS))
            self.next.append(choice(self.SHAPES))
            self.next.append(choice(self.COLORS))
            self.begin = False
        else:
            nxt = self.next[:]
            self.current[0] = nxt[0]
            self.current[1] = nxt[1]
            self.next.pop()
            self.next.pop()
            self.next.append(choice(self.SHAPES))
            self.next.append(choice(self.COLORS))

    def __update(self):
        # DRAW THE BOARD
        pygame.draw.rect(self.screen, self.BG_COLOR, (0, 0, self.shape_width * 10, self.shape_width * 20))
        # DRAW ANY OTHER PAST CUBES
        for i, cube in enumerate(self.history_shapes):
            x, y = cube[1] * self.shape_width, cube[0] * self.shape_width
            pygame.draw.rect(self.screen, self.history_colors[i], (x, y, self.shape_width, self.shape_width))
        # DRAW CURRENT SHAPE
        self.shape.draw()
        pygame.display.update()

    def __check_collision(self):
        if self.shape.collision(self.board):
            # CHECKS IF THE COLLISION HAPPENED ABOVE THE MAP IF IT HAPPENED THEN RESETS THE GAME
            for cube in self.shape.positions:
                if cube[0] == -1:
                    self.__update()
                    pygame.time.delay(1000)
                    self.__reset()
                    return
            # CHECKS FURTHER EVENTS WITHIN 0.4 SECONDS
            start = time()
            pressed = False
            self.dellay = self.DELLAY
            while time() - start < 0.4:
                pressed = self.__check_events()
                self.__update()
                if pressed and self.shape.collision(self.board):
                    break
                elif pressed and not self.shape.collision(self.board):
                    return

            # COLLISION IS STORED IN OTHER VARIABLES
            can_be_line = False
            for cube in self.shape.positions:
                self.history_shapes.append(cube)
                self.history_colors.append(self.shape.color)
                self.board[cube[0]][cube[1]] = 1
                self.counter[cube[0]] += 1
                if self.counter[cube[0]] == 10:
                    can_be_line = True
            # CHECKS IF IT IS AT LEAST A LINE IF IT IS THEN DELETES IT
            if can_be_line:
                for i in range(20):
                    if self.counter[i] == 10:
                        self.board = [[0 for j in range(10)] for i in range(20)]
                        self.__delete_row(i)
            # PICK OTHER RANDOM SHAPE AND CREATE IT
            self.__pick_rand()
            self.shape = Shape(self.screen, self.shape_width, self.current[0], self.current[1])
            self.shape.create()

    def __delete_row(self, row):
        # SHIFTING COUNTER TO THE RIGHT
        for i in range(row, 0, -1):
            self.counter[i] = self.counter[i - 1]
        self.counter[0] = 0
        # DELETING ROW ELEMENTS FROM HISTORY SHAPES AND COLORS
        l = []
        for i in range(0, len(self.history_shapes)):
            if self.history_shapes[i][0] == row:
                l.append(i)
        for j in range(len(l)):
            del self.history_shapes[l[j]]
            del self.history_colors[l[j]]
            for h in range(j + 1, len(l)):
                l[h] -= 1
        # SHIFTING ELEMENTS TO THE BOTTOM AND CHANGING THE BOARD
        for cube in self.history_shapes:
            if cube[0] < row:
                cube[0] += 1
            self.board[cube[0]][cube[1]] = 1

    def __reset(self):
        self.begin = True
        self.current = []
        self.next = []
        self.__pick_rand()
        self.shape = Shape(self.screen, self.shape_width, self.current[0], self.current[1])
        self.shape.create()
        self.board = [[0 for j in range(10)] for i in range(20)]
        self.history_shapes = []
        self.history_colors = []
        self.counter = [0 for _ in range(20)]
        self.time = 0
        self.dellay = self.DELLAY


class Shape:
    def __init__(self, screen, width, shape, color):
        # Shape characteristics
        self.positions = []
        self.color = color
        self.shape = shape
        self.head = None
        self.angle = 90
        self.shape_width = width

        # Screen characteristics
        self.screen = screen
        self.screen_width = screen.get_rect().width
        self.screen_height = screen.get_rect().height

    def create(self):
        # FILLING INITIAL POSITIONS WITH A LIST OF [ROW, COLUMN]
        if self.shape == 'I':
            self.positions.append([-1, 5])
            self.positions.append([-2, 5])
            self.positions.append([-3, 5])
            self.positions.append([-4, 5])
            self.head = self.positions[2]
        elif self.shape == 'J':
            self.positions.append([-1, 4])
            self.positions.append([-1, 5])
            self.positions.append([-2, 5])
            self.positions.append([-3, 5])
            self.head = self.positions[2]
        elif self.shape == 'L':
            self.positions.append([-1, 5])
            self.positions.append([-1, 6])
            self.positions.append([-2, 5])
            self.positions.append([-3, 5])
            self.head = self.positions[2]
        elif self.shape == 'O':
            self.positions.append([-1, 5])
            self.positions.append([-1, 6])
            self.positions.append([-2, 5])
            self.positions.append([-2, 6])
        elif self.shape == 'Z':
            self.positions.append([-1, 5])
            self.positions.append([-1, 6])
            self.positions.append([-2, 5])
            self.positions.append([-2, 4])
            self.head = self.positions[2]
        elif self.shape == 'T':
            self.positions.append([-1, 5])
            self.positions.append([-2, 4])
            self.positions.append([-2, 5])
            self.positions.append([-2, 6])
            self.head = self.positions[2]
        elif self.shape == 'S':
            self.positions.append([-1, 4])
            self.positions.append([-1, 5])
            self.positions.append([-2, 5])
            self.positions.append([-2, 6])
            self.head = self.positions[2]

    def move_down(self):
        for cube in self.positions:
            cube[0] += 1

    def move_left(self, board):
        # CHECKS IF MOVING LEFT IT'S NOT GETTING OFF THE SCREEN
        for cube in self.positions[:]:
            if cube[1] - 1 == -1:
                return
            # CHECKS IF MOVING LEFT INTERACT WITH OTHER PAST SHAPES
            if cube[0] >= 0:
                if board[cube[0]][cube[1] - 1] != 0:
                    return

        # IF IT HAS NOT RETURNED YET AND PASSED ALL TESTS THEN MOVE LEFT
        for cube in self.positions:
            cube[1] -= 1

    def move_right(self, board):
        # CHECKS IF MOVING RIGHT IT'S NOT GETTING OFF THE SCREEN
        for cube in self.positions[:]:
            if cube[1] + 1 == 10:
                return
            # CHECKS IF MOVING LEFT INTERACT WITH OTHER PAST SHAPES
            if cube[0] >= 0:
                if board[cube[0]][cube[1] + 1] != 0:
                    return

        # IF IT HAS NOT RETURNED YET AND PASSED ALL TESTS THEN MOVE LEFT
        for cube in self.positions:
            cube[1] += 1

    def rotate(self, board):
        # IF IT'S NOT I OR O ROTATE BY 90 AFTER THE TEST HAS BEEN PASSED
        if self.shape != 'O' and self.shape != 'I':
            if self.__can_rotate(board):
                self.__give_rotation()
        # IF I ROTATES WE SWITCH ANGLE BETWEEN 90 AND 270/-90 TO VISUALIZE BETTER
        elif self.shape == 'I':
            if self.__can_rotate(board):
                self.__give_rotation()
                self.__switch_angle()

    def __give_rotation(self):
        if self.angle == 90:
            for cube in self.positions:
                tempy = cube[0] - self.head[0]
                tempx = cube[1] - self.head[1]
                cube[0] = self.head[0] - tempx
                cube[1] = self.head[1] + tempy
        elif self.angle == 270:
            for cube in self.positions:
                tempy = cube[0] - self.head[0]
                tempx = cube[1] - self.head[1]
                cube[0] = self.head[0] + tempx
                cube[1] = self.head[1] - tempy

    def __can_rotate(self, board):
        # CHECKS IF ROTATION IS GOING TO GET THE PIECE OF THE SCREEN OR IT'S GOING TO INTERACT WITH OTHER PIECES
        if self.angle == 90:
            for cube in self.positions[:]:
                tempy = cube[0] - self.head[0]
                tempx = cube[1] - self.head[1]
                y = self.head[0] - tempx
                x = self.head[1] + tempy
                if x < 0 or x > 9:
                    return False
                if board[y][x] != 0:
                    return False
        elif self.angle == 270:
            for cube in self.positions[:]:
                tempy = cube[0] - self.head[0]
                tempx = cube[1] - self.head[1]
                y = self.head[0] + tempx
                x = self.head[1] - tempy
                if x < 0 or x > 9:
                    return False
                if board[y][x] != 0:
                    return False
        return True

    def __switch_angle(self):
        if self.angle == 90:
            self.angle = 270
        else:
            self.angle = 90

    def draw(self):
        for cube in self.positions:
            x, y = cube[1] * self.shape_width, cube[0] * self.shape_width
            pygame.draw.rect(self.screen, self.color, (x, y, self.shape_width, self.shape_width))

    def collision(self, board):
        for cube in self.positions[:]:
            if cube[0] == 19:
                return True

            elif cube[0] >= 0:
                if board[cube[0] + 1][cube[1]] != 0:
                    return True

        return False


if __name__ == '__main__':
    tg = TetrisGame()
    tg.run_game()

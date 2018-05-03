from tkinter import *
from tkinter import  messagebox
import sys
import time
from random import randint

HEIGHT = 12
WIDTH = 12

FIELD_SIZE = HEIGHT * WIDTH

HEAD = 0

FOOD = 0
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)      # if HEIGHT = WIDTH = 5, UNDEFINED = 36
SNAKE = 2 * UNDEFINED              # if UNDEFINED = 36, SNAKE = 72

LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH

ERR = -1111

MAP = [0] * FIELD_SIZE
SNAKE_BODY = [0] * (FIELD_SIZE + 1)
SNAKE_SIZE = 1
SNAKE_BODY[0] = 0

# 用于安全检测的虚拟蛇信息
V_MAP = [0] * FIELD_SIZE
V_SNAKE_BODY = [0] * (FIELD_SIZE + 1)
V_SNAKE_SIZE = 1
V_SNAKE_BODY[0] = 0         # 数组中的第一个元素一定是 0，这是句废话

Snake_Food = ERR
BEST_MOVE = ERR

MOVE = [LEFT, RIGHT, UP, DOWN]
KEY_FIRST = "UP"
SCORE = 1

# 颜色
COLOR_HEX = ["F", "C", "9", "6", "3", "0"]

class Grid(object):
    def __init__(self, master=None, window_width=WIDTH*25, window_height=HEIGHT*25, grid_width=25, offset=20):
        self.height = window_height
        self.width = window_width
        self.grid_width = grid_width
        self.offset = offset
        self.grid_x = self.width / self.grid_width
        self.grid_y = self.height / self.grid_width
        self.bg = "#EBEBEB"

        self.canvas = Canvas(master, width=self.width+2*self.offset, height=self.height+2*self.offset, bg=self.bg)

        self.canvas.pack()
        self.grid_list()

    def draw(self, pos, color):
        x = pos[0] * self.grid_width + self.offset
        y = pos[1] * self.grid_width + self.offset
        self.canvas.create_rectangle(x, y, x+self.grid_width, y+self.grid_width, fill=color, outline=self.bg)

    def grid_list(self):
        grid_list = []

        for y in range(0, int(self.grid_y)):
            for x in range(0, int(self.grid_y)):
                grid_list.append((x, y))

        self.grid_list = grid_list

class Food(object):
    def __init__(self, Grid):
        self.grid = Grid
        self.color = "#23D978"
        self.set_pos()

    def set_pos(self):
        global Snake_Food
        x = randint(0, self.grid.grid_x - 1)
        y = randint(0, self.grid.grid_y - 1)
        Snake_Food = y * WIDTH + x
        self.pos = (x, y)

    def display(self):
        self.grid.draw(self.pos, self.color)

class Snake(object):
    def __init__(self, grid):
        self.grid = grid
        self.body = [(0, 0)]
        self.direction = "UP"
        self.status = ['run', 'stop']
        self.speed = 1
        self.color = "#FFFFFF"
        # self.color = "#000000"
        self.food = Food(self.grid)
        self.display_food()
        self.gameover = False
        self.score = 1

    def available_grid(self):
        return [i for i in self.grid.grid_list if i not in self.body[2:]]

    def change_direction(self, direction):
        self.direction = direction

    def display(self):
        for (x, y) in self.body:
            self.grid.draw((x, y), self.color)

    def display_food(self):
        while self.food.pos in self.body:
            self.food.set_pos()
        self.food.display()

    # 用于自动运行的方法
    def is_cell_free(self, idx, psize, psnake):
        return not (idx in psnake[:psize])

    def is_move_possible(self, idx, move):
        global MAP
        flag = False
        if move == LEFT:
            flag = True if idx % WIDTH > 0 else False
        elif move == RIGHT:
            flag = True if idx % WIDTH < WIDTH - 1 else False
        elif move == UP:
            flag = True if idx > WIDTH - 1 else False
        elif move == DOWN:
            flag = True if idx < (FIELD_SIZE - WIDTH) else False

        # 当蛇移动的位置，在一个单位距离内存在蛇身
        # if MAP

        return flag

    def board_reset(self, psnake, psize, pboard):
        for i in range(FIELD_SIZE):
            if i == Snake_Food:
                pboard[i] = FOOD
            elif self.is_cell_free(i, psize, psnake):
                pboard[i] = UNDEFINED
            else:
                pboard[i] = SNAKE

    def board_refresh(self, pfood, psnake, pboard):
        queue = []
        queue.append(pfood)         # 目标第一个入栈
        inqueue = [0] * FIELD_SIZE
        found = False
        while len(queue) != 0:
            idx = queue.pop(0)

            if inqueue[idx] == 1:
                continue
            inqueue[idx] = 1

            for i in range(4):
                if self.is_move_possible(idx, MOVE[i]):
                    print("idx+MOVE[i]=%d,psnake[HEAD]=%d",(idx+MOVE[i],psnake[HEAD]))
                    if idx + MOVE[i] == psnake[HEAD]:
                        found = True
                        # break
                        print("----是否运行----")

                    # print('i=%d MOVE[i]=%s idx + MOVE[i]=%d pboard[idx + MOVE[i]]=%d', i, MOVE[i], idx + MOVE[i],pboard[idx + MOVE[i]])

                    if pboard[idx + MOVE[i]] < SNAKE:
                        if pboard[idx + MOVE[i]] > pboard[idx] + 1:
                            pboard[idx + MOVE[i]] = pboard[idx] + 1

                        if inqueue[idx + MOVE[i]] == 0:
                            queue.append(idx + MOVE[i])

            # if found == True:
            #     break

        return found

    def choose_shorest_safe_move(self, psnake, pboard):
        best_move = ERR
        min = SNAKE

        for i in range(4):
            if self.is_move_possible(psnake[HEAD], MOVE[i]) and pboard[psnake[HEAD] + MOVE[i]] < min:
                min = pboard[psnake[HEAD] + MOVE[i]]
                best_move = MOVE[i]

        return best_move

    def choose_longest_safe_move(self, psnake, pboard):
        best_move = ERR
        max = -1

        for i in range(4):
            print("=====最长路径问题=====")
            # print("pboard[psnake[%d]+MOVE[%d]]=%d,max=%d"%(HEAD,i,pboard[psnake[HEAD]+MOVE[i]],max))
            if self.is_move_possible(psnake[HEAD], MOVE[i]) and UNDEFINED > pboard[psnake[HEAD] + MOVE[i]] > max:
                max = pboard[psnake[HEAD] + MOVE[i]]
                best_move = MOVE[i]

        if best_move == ERR:
            print("....................")
            print("最长路径没有选择")
        return best_move

    # 仔细研究
    def is_tail_inside(self):
        global V_MAP, V_SNAKE_BODY, Snake_Food, V_SNAKE_SIZE
        V_MAP[V_SNAKE_BODY[V_SNAKE_SIZE - 1]] = 0
        V_MAP[Snake_Food] = SNAKE
        result = False

        if self.board_refresh(V_SNAKE_BODY[V_SNAKE_SIZE - 1], V_SNAKE_BODY, V_MAP):
            result = True
            # for i in range(4):
            #     if self.is_move_possible(V_SNAKE_BODY[HEAD], MOVE[i]) and\
            #         V_SNAKE_BODY[HEAD] + MOVE[i] == V_SNAKE_BODY[V_SNAKE_SIZE - 1] and\
            #         V_SNAKE_SIZE > 3:
                # if self.is_move_possible(V_SNAKE_BODY[HEAD], MOVE[i]) and \
                #                 V_SNAKE_SIZE > 0:
                #     print("-----追尾判断-----")
                #     print("V_SNAKE_BODY[%d]+MOVE[%d]=%d,V_SNAKE_BODY[%d]=%d"%(HEAD,i,V_SNAKE_BODY[HEAD]+MOVE[i],V_SNAKE_SIZE-1,V_SNAKE_BODY[V_SNAKE_SIZE-1]))
                #     result = False

        return result

    # 不管蛇身阻挡，朝向蛇尾方向运行的理解。。？？那不是直接OVER了
    def follow_tail(self):
        global V_MAP, V_SNAKE_BODY, Snake_Food, V_SNAKE_SIZE
        V_SNAKE_SIZE = SNAKE_SIZE
        V_SNAKE_BODY = SNAKE_BODY[:]

        self.board_reset(V_SNAKE_BODY, V_SNAKE_SIZE, V_MAP)

        V_MAP[V_SNAKE_BODY[V_SNAKE_SIZE - 1]] = FOOD
        V_MAP[Snake_Food] = SNAKE

        self.board_refresh(V_SNAKE_BODY[V_SNAKE_SIZE - 1], V_SNAKE_BODY, V_MAP)

        # V_MAP[V_SNAKE_BODY[V_SNAKE_SIZE - 1]] = SNAKE

        print("--------------------------")
        print("在追随尾部的过程中失去方向")
        print("choose_longest_safe_move=%d" % (self.choose_longest_safe_move(V_SNAKE_BODY, V_MAP)))
        print("==========================")

        return self.choose_longest_safe_move(V_SNAKE_BODY, V_MAP)

    def any_possible_move(self):
        global Snake_Food, SNAKE_BODY, SNAKE_SIZE, MAP
        best_move = ERR
        min = SNAKE

        self.board_reset(SNAKE_BODY, SNAKE_SIZE, MAP)
        self.board_refresh(Snake_Food, SNAKE_BODY, MAP)

        for i in range(4):
            if self.is_move_possible(V_SNAKE_BODY[HEAD], MOVE[i]) and V_MAP[V_SNAKE_BODY[HEAD] + MOVE[i]] < min:
                min = V_MAP[V_SNAKE_BODY[HEAD] + MOVE[i]]
                best_move = MOVE[i]

        return best_move

    def shift_array(self, arr, size):
        for i in range(size, 0, -1):
            arr[i] = arr[i - 1]

    # 当“吃到食物标记”不为真，会死循环下去。需要分析一下
    def virtual_shortest_move(self):
        global SNAKE_BODY, MAP, SNAKE_SIZE, V_SNAKE_BODY, V_MAP, V_SNAKE_SIZE, Snake_Food
        V_SNAKE_SIZE = SNAKE_SIZE
        V_SNAKE_BODY = SNAKE_BODY[:]
        V_MAP = MAP[:]

        self.board_reset(V_SNAKE_BODY, V_SNAKE_SIZE, V_MAP)

        print("================")
        print("吃到食物之前的V_MAP")
        # 显示V_MAP
        for i in range(WIDTH * HEIGHT):
            if i > 0 and i % WIDTH == 0:
                print()
            print(V_MAP[i], end=' ')
        print()
        print("00000000000000000")

        food_eated = False
        while not food_eated:
            self.board_refresh(Snake_Food, V_SNAKE_BODY, V_MAP)

            move = self.choose_shorest_safe_move(V_SNAKE_BODY, V_MAP)

            self.shift_array(V_SNAKE_BODY, V_SNAKE_SIZE)

            V_SNAKE_BODY[HEAD] += move

            if V_SNAKE_BODY[HEAD] == Snake_Food:
                V_SNAKE_SIZE += 1
                self.board_reset(V_SNAKE_BODY, V_SNAKE_SIZE, V_MAP)
                V_MAP[Snake_Food] = SNAKE
                food_eated = True
            else:
                V_MAP[V_SNAKE_BODY[HEAD]] = SNAKE
                V_MAP[V_SNAKE_BODY[V_SNAKE_SIZE]] = UNDEFINED

        # print("********************")
        # print("吃到食物之hou的V_MAP")
        # # 显示V_MAP
        # for i in range(WIDTH * HEIGHT):
        #     if i > 0 and i % WIDTH == 0:
        #         print()
        #     print(V_MAP[i], end=' ')
        # print()
        # print("00000000000000000")

    # 问题好像出在这里
    def find_safe_way(self):
        global SNAKE_BODY, MAP, V_SNAKE_BODY, V_MAP
        safe_move = ERR

        self.virtual_shortest_move()

        if self.is_tail_inside():
            # print("YYYYY虚拟运行中通过")
            return self.choose_shorest_safe_move(SNAKE_BODY, MAP)
            # return self.follow_tail()

        # print("NNNNN虚拟运行不中通过")
        # safe_move = self.choose_longest_safe_move(SNAKE_BODY, MAP)
        safe_move = self.follow_tail()

        return safe_move

    # 移动函数
    def move(self):
        global SNAKE_BODY, SNAKE_SIZE, V_SNAKE_BODY, V_SNAKE_SIZE, MAP, V_MAP

        self.board_reset(SNAKE_BODY, SNAKE_SIZE, MAP)
        # 蛇尾应当视作空出
        # MAP[SNAKE_BODY[SNAKE_SIZE - 1]] = UNDEFINED

        # print("================")
        # print("MAP")
        # # 显示V_MAP
        # for i in range(WIDTH * HEIGHT):
        #     if i > 0 and i % WIDTH == 0:
        #         print()
        #     print(MAP[i], end=' ')
        # print()
        # print("================")

        # print("***入栈的食物位置：%d***",(Snake_Food))
        if self.board_refresh(Snake_Food, SNAKE_BODY, MAP):
            best_move = self.find_safe_way()
            # print("BFS best_move=%d" % (best_move))
        else:
            best_move = self.follow_tail()
            # print("else BFS best_move=%d" % (best_move))

        # 这里应该也是使用虚拟蛇操作
        if best_move == ERR:
            best_move = self.any_possible_move()
            # print("possible best_move=%d" % (best_move))

        if best_move != ERR:
            if best_move == -1: key = "Left"
            elif best_move == 1: key = "Right"
            elif best_move == WIDTH: key = "Down"
            elif best_move == -WIDTH: key = "Up"
        else:
            self.status.reverse()
            self.gameover = True
            message = messagebox.showinfo("GAME OVER", "Your Score: %d" % self.score)
            if message == 'ok':
                sys.exit()

        self.change_direction(key)

        head = self.body[0]
        if self.direction == 'Up':
            new = (head[0], head[1] - 1)
        elif self.direction == 'Down':
            new = (head[0], head[1] + 1)
        elif self.direction == 'Left':
            new = (head[0] - 1, head[1])
        else:
            new = (head[0] + 1, head[1])

        if not self.food.pos == new:
            self.body.insert(0, new)
            pop = self.body.pop()
            self.grid.draw(pop, self.grid.bg)

            # 移动后没有吃到食物
            for i in range(SNAKE_SIZE, 0, -1):
                SNAKE_BODY[i] = SNAKE_BODY[i - 1]
            SNAKE_BODY[HEAD] = new[1] * WIDTH + new[0]
            # SNAKE_BODY[SNAKE_SIZE] = UNDEFINED          # 新增，移动后吃到食物和移动后吃不到食物地图没有更新
            MAP[SNAKE_BODY[HEAD]] = SNAKE  # 而且，吃食物、没吃食物，地图的更新方式有区别
            MAP[SNAKE_BODY[SNAKE_SIZE]] = UNDEFINED  # 蛇身体的更新方式，移动后吃到食物，食物变成头部
            # 并产生新的食物位置
            # 移动后没有吃到食物，蛇头为前进的位置，
        else:
            self.body.insert(0, new)

            for i in range(SNAKE_SIZE, 0, -1):
                SNAKE_BODY[i] = SNAKE_BODY[i - 1]
            SNAKE_BODY[HEAD] = Snake_Food
            MAP[Snake_Food] = SNAKE

            self.display_food()

            MAP[Snake_Food] = FOOD

            self.score += 1
            SNAKE_SIZE += 1
            V_SNAKE_SIZE += 1

            # 移动后吃到食物
            # for i in range(SNAKE_SIZE, 0, -1):
            #     SNAKE_BODY[i] = SNAKE_BODY[i - 1]
            # SNAKE_BODY[HEAD] = Snake_Food
            # MAP[Snake_Food] = SNAKE
            # MAP[Snake_Food] = FOOD
        # print("========================")
        # print("++++++++++++++++++++++++")
        # print("The score: %d" % (self.score))
        # print("++++++++++++++++++++++++")
        # print("========================")
        if self.score == WIDTH * HEIGHT:
            self.status.reverse()
            self.gameover = True
            message = messagebox.showinfo("You Win", "Your Score: %d" % self.score)
            if message == 'ok':
                sys.exit()

        if not new in self.available_grid():
            print('判断错误')
            self.status.reverse()
            self.gameover = True
        else:
            # 修改颜色
            # c_int = SNAKE_SIZE % 16
            # if c_int == 0:  c_char = '0'
            # elif c_int == 1: c_char = '1'
            # elif c_int == 2: c_char = '2'
            # elif c_int == 3: c_char = '3'
            # elif c_int == 4: c_char = '4'
            # elif c_int == 5: c_char = '5'
            # elif c_int == 6: c_char = '6'
            # elif c_int == 7: c_char = '7'
            # elif c_int == 8: c_char = '8'
            # elif c_int == 9: c_char = '9'
            # elif c_int == 10: c_char = 'A'
            # elif c_int == 11: c_char = 'B'
            # elif c_int == 12: c_char = 'C'
            # elif c_int == 13: c_char = 'D'
            # elif c_int == 14: c_char = 'E'
            # elif c_int == 15: c_char = 'F'

            # 1、3、5，2、4、6
            # print(c_char)
            # if self.score % 4 == 0:
            #     self.color = self.color[:1] + c_char + self.color[2:]
            #     self.color = self.color[:2] + c_char + self.color[3:]
            # else:
            #     # self.color = self.color[:4] + c_char + self.color[5:]
            #     # self.color = self.color[:5] + c_char + self.color[6:]
            #     self.color = self.color[:6] + c_char + self.color[7:]

            # if self.score / 6 == 0:
            # print(COLOR_HEX[(self.score - 1) % 6])
            self.color = self.color[:1] + COLOR_HEX[int(self.score / 36) % 6] + self.color[2:]
            self.color = self.color[:2] + COLOR_HEX[int(self.score / 36) % 6] + self.color[3:]
            self.color = self.color[:3] + COLOR_HEX[int(self.score / 6) % 6] + self.color[4:]
            self.color = self.color[:4] + COLOR_HEX[int(self.score / 6) % 6] + self.color[5:]
            self.color = self.color[:5] + COLOR_HEX[(self.score - 1) % 6] + self.color[6:]
            self.color = self.color[:6] + COLOR_HEX[(self.score - 1) % 6] + self.color[7:]
            print(self.color)

            self.grid.draw(new, color=self.color)

            # for i in range(SNAKE_SIZE):
            #     i += SNAKE_SIZE
            #     self.color = self.color[:1] + COLOR_HEX[int(i / 36) % 6] + self.color[2:]
            #     self.color = self.color[:2] + COLOR_HEX[int(i / 36) % 6] + self.color[3:]
            #     self.color = self.color[:3] + COLOR_HEX[int(i / 6) % 6] + self.color[4:]
            #     self.color = self.color[:4] + COLOR_HEX[int(i / 6) % 6] + self.color[5:]
            #     self.color = self.color[:5] + COLOR_HEX[(i - 1) % 6] + self.color[6:]
            #     self.color = self.color[:6] + COLOR_HEX[(i - 1) % 6] + self.color[7:]
            #     self.grid.draw(self.body[i - SNAKE_SIZE], color=self.color)

class SnakeAI(Frame):
    def __init__(self, master=None, *args, **kwargs):
        Frame.__init__(self, master)
        self.master = master
        self.grid = Grid(master=master, *args, **kwargs)
        self.snake = Snake(self.grid)
        self.snake.display()

    def run(self):
        self.snake.move()
        if self.snake.gameover is True:
            message = messagebox.showinfo("GAME OVER", "Your Score: %d" % self.snake.score)
            if message == 'ok':
                sys.exit()
        self.after(self.snake.speed, self.run)


if __name__ == '__main__':
    root = Tk()
    snakegame = SnakeAI(root)
    snakegame.run()
    snakegame.mainloop()







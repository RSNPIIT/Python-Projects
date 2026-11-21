from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros
from gym_super_mario_bros.actions import COMPLEX_MOVEMENT
import numpy as np
import cv2
import random
import math
import time

class Game:
    def __init__(self):
        self.env = gym_super_mario_bros.make('SuperMarioBros-4-1-v0', render_mode='rgb_array')
        self.env = JoypadSpace(self.env, COMPLEX_MOVEMENT)
        self.done = True
        self.state = None
        self.info = None
        self.reward = None
        self.terminated = None
        self.truncated = None
        self.ram = self.env.unwrapped.ram
        self.grid = None

    def tile_loc_to_ram_address(self,x, y):
        page = x // 16
        x_loc = x % 16
        y_loc = page * 13 + y
        address = 0x500 + x_loc + y_loc * 16
        return address

    def get_grid(self):
        screen_size_x = 16
        screen_size_y = 13

        mario_level_x = int(self.ram[0x6d]) * 256 + int(self.ram[0x86])
        mario_x = int(self.ram[0x3ad])
        mario_y = int(self.ram[0x3b8]) + 16

        x_start = mario_level_x - mario_x

        rendered_screen = np.zeros((screen_size_y, screen_size_x))
        screen_start = int(np.rint(x_start / 16))

        for i in range(screen_size_x):
            for j in range(screen_size_y):
                x_loc = (screen_start + i) % (screen_size_x * 2)
                y_loc = j
                address = self.tile_loc_to_ram_address(x=x_loc, y=y_loc)
                if self.ram[address] != 0:
                    rendered_screen[j, i] = 1

        x_loc = (mario_x + 8) // 16
        y_loc = (mario_y - 32) // 16
        if x_loc < 16 and y_loc < 13:
            rendered_screen[y_loc, x_loc] = 2

        for i in range(5):
            if self.ram[0xF + i] == 1:
                enemy_x = int(self.ram[0x6e + i]) * 256 + int(self.ram[0x87 + i]) - x_start
                enemy_y = int(self.ram[0xcf + i])
                x_loc = (enemy_x + 8) // 16
                y_loc = (enemy_y + 8 - 32) // 16
                if 0 <= x_loc < 16 and 0 <= y_loc < 13:
                    rendered_screen[y_loc, x_loc] = -1
        return rendered_screen

def tile(frames, cols):
    h, w, _ = frames[0].shape
    blank = np.zeros((h, w, 3), dtype=np.uint8)
    padded = frames + [blank] * (-len(frames) % cols)
    rows = [np.hstack(padded[i:i+cols]) for i in range(0, len(padded), cols)]
    return np.vstack(rows)

def step_games_and_return_obstacles(elements, show_all_games):
    obst_grids = []
    frames = []
    for e in elements:
        if e.game.done:
            e.game.state, e.game.info = e.game.env.reset()
            e.game.done = False
        print(e.game.info)
        action = e.input
        e.game.state, e.game.reward, e.game.terminated, e.game.truncated, e.game.info = e.game.env.step(action)
        e.game.done = e.game.terminated or e.game.truncated
        e.game.grid = e.game.get_grid()
        obst_grids.append(e.game.grid)
        if show_all_games:
            frames.append(e.game.env.render())
    # time.sleep(0.1)
    return obst_grids, frames

def render_games(frames, cols, gen_count):
    screen = tile(frames, cols=cols)
    screen_height, screen_width, _ = screen.shape
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.putText(screen, f"GEN {gen_count}", (10, screen_height - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow('Like and Subscribe', screen)
    cv2.waitKey(1)

def close_games(elements, show_all_games):
    for e in elements:
        e.game.env.close()
    if show_all_games:
        cv2.destroyAllWindows()



# games = []
# create_games(2)
# run_games(games,show_all_games=True)

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import random

# Initializing Pygame -> Makes all available in the userland
pygame.init()

# Display surface
WIDTH = 600
HEIGHT = 600
displ = pygame.display.set_mode((
    WIDTH,
    HEIGHT
))
pygame.display.set_caption("Captain America")

HALF_X = WIDTH // 2
HALF_Y = HEIGHT // 2
ARENA = (HALF_X, HALF_Y)

# RGB Tuples for Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Changing the Background
displ.fill(BLUE)
COL_LIS = [BLACK , WHITE, RED, YELLOW, CYAN, MAGENTA, GREEN, WHITE, YELLOW, MAGENTA]
random.shuffle(COL_LIS)

# Making successive circles here (Ensuring that the current colour can never be the last one)
radius = HALF_X
last_col = None
for i in range(10):
    current_col = random.choice(COL_LIS)

    # Picking a colour unless a colour that's different from the others
    while current_col == last_col:
        current_col = random.choice(COL_LIS)
    
    # Updating the last colour herein
    last_col = current_col

    # Making the circles herein
    if radius > 0:
        pygame.draw.circle(displ, current_col, ARENA, radius, 0)
    radius -= 30

# Making the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()

# Safely end the game
pygame.quit()
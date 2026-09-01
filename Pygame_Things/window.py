import os

# This is so as to hide all the clunky prompts
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import sys

# Making all functions in Pygame available in the userland
pygame.init()

# Building the Screen (Arguments as a Tuple of Width and Height both in pixels by default as args)
screen = pygame.display.set_mode((800, 400))

# This just gives the title to the window
pygame.display.set_caption("Game")

# Sets the ceiling of the Animation (By Itself it does nothing)
clock = pygame.time.Clock()

# Sample Red Coloured Test surface
sky_surface = pygame.image.load('graphics/skyblue.png')

# But we see that the Screen Display soon ends as the program terminates
while True:
    # The Inner File allows the user to close the file by the cross button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Imcorporate the Test surface unto the display surface
    screen.blit(sky_surface, (0, 0))

    # This is a boilerplate to Update the Screen as the mainloop that keeps the screen on
    pygame.display.update()
    clock.tick(60)
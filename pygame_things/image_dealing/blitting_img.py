import os as o
o.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

pygame.init()
WIN_WID = 600
WIN_HEI = 300
BLUE = (0, 0, 255)
FILE_IMG = "dragon_img.png"
FLP_FILE = "dragon_rgt.png"

displ = pygame.display.set_mode(
    (WIN_WID, WIN_HEI)
)
displ.fill(BLUE)
pygame.display.set_caption("Blitting")

# Loading the Image here (returns as as surface object with the image drawn on it)
# We use the rect method to essentially positon the image
drag_lft = pygame.image.load(FILE_IMG)
drag_lft_img = drag_lft.get_rect()
drag_lft_img.topleft = (0, 0)
# displ.blit()

drag_rgt = pygame.image.load(FLP_FILE)
drag_rgt_img = drag_rgt.get_rect()
drag_rgt_img.topright = (WIN_WID, 0)

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
    # The general method to blit an image to a display surface
    displ.blit(
        drag_lft,
        drag_lft_img
    )
    displ.blit(
        drag_rgt,
        drag_rgt_img
    )
    pygame.display.update()

pygame.quit()
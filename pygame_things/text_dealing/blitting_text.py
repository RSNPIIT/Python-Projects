import os as o
o.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
pygame.init()
WIN_WID = 600
WIN_HEI = 300
GREEN = (0, 255, 0)
DARKGREEN = (10, 50, 10)
BLACK = (0, 0, 0)

try:
    displ = pygame.display.set_mode(
        (WIN_WID, WIN_HEI)
    )
    displ.fill(GREEN)
    pygame.display.set_caption("Blitting Text")

    # Commented this section (It helps to see how many pygame compatible fonts are there in the system) but for some reason this tends to glitch on MacOS
    # all_font = pygame.font.get_fonts()
    # for idx, font in enumerate(all_font):
    #     print(f"{idx + 1} -> {font}")
    #     if idx == len(all_font):
    #         break

    system_font = pygame.font.SysFont(None, 64)
    custom_font = pygame.font.Font("SuperCrown-6Rwmv.ttf", 64)

    # Define Text
    system_text = system_font.render("Dragons Rule", True, BLACK, DARKGREEN)
    system_text_rect = system_text.get_rect()
    system_text_rect.center = (WIN_WID // 2, WIN_HEI // 2)

    custom_text = custom_font.render("Move the Dragon soon!", True, BLACK)
    custom_text_rect = custom_text.get_rect()
    custom_text_rect.center = (WIN_WID // 2, (WIN_HEI // 2) + 100)

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
        displ.blit(
            system_text,
            system_text_rect
        )
        displ.blit(
            custom_text,
            custom_text_rect
        )
        pygame.display.update()

except (KeyboardInterrupt, EOFError):
    print("\nQuitting\n")
    o.system("cls" if o.name == "nt" else "clear")

finally:
    pygame.quit()
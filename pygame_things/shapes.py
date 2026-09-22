import pygame

# Initializing the Pygame Library
pygame.init()

# Setting the Game dimentions here
WIDTH = 600
HEIGHT = 600
displ = pygame.display.set_mode((
    WIDTH,
    HEIGHT
))
pygame.display.set_caption("Setting Shapes")

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

# Draw Various Geometric Shapes in our Display
# Draw Lines -> Line(display surface, colour, starting coordinate tuple, ending coordinate tuple, pen width)
pygame.draw.line(displ, RED, (0,0), (100,100), 5)
pygame.draw.line(displ, GREEN, (100,100), (200,200), 5)

# Colour -> surface , colour ,center coordinates , radius , thickess 0 if fully filled
pygame.draw.circle(displ, WHITE, (WIDTH // 2 , HEIGHT // 2), 200, 6)
pygame.draw.circle(displ, CYAN, (WIDTH // 2 , HEIGHT // 2), 150, 0)

# Rectangle -> surface, color, (top-left-x, top-left-y, width , height)
pygame.draw.rect(displ, MAGENTA ,(500, 0, 100, 100))
pygame.draw.rect(displ, YELLOW, (500, 100, 50, 100))

# Setting the mainloop for the game here
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Updating the display
    pygame.display.update()

pygame.quit()
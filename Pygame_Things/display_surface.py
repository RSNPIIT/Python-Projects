import pygame

# Initializing Pygame -> Makes all available in the userland
pygame.init()

# Display surface
WIDTH = 600
HEIGHT = 300
display_surface = pygame.display.set_mode((
    WIDTH,
    HEIGHT
))
pygame.display.set_caption("My Display")

# Making the game loop
running = True
while running:
    # Loop through list of events that have occurres
    for event in pygame.event.get():
        # print(event)
        # Quit if the user clicks the cross to close
        if event.type == pygame.QUIT:
            running = False

# Safely end the game
pygame.quit()
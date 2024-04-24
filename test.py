import pygame
import os
import gif_pygame as gif

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

# Load GIF file
assets_dir = os.path.join("assets")
states_dir = os.path.join(assets_dir, "states")
title = os.path.join(states_dir, "title.gif")
gif_obj = gif.load(title)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    gif_obj.render(screen, (0, 0))
    pygame.display.flip()

    clock.tick(30)

pygame.quit()

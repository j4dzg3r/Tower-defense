import pygame


pygame.init()

size = width, height = 1110, 960
screen = pygame.display.set_mode(size)
weapon_group = pygame.sprite.Group()
foundation_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
health_bar_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()

clock = pygame.time.Clock()


from subpackages.map import Map


def main():
    running = True

    map = Map("data/levels/level_1.txt", weapon_group, foundation_group, enemy_group, health_bar_group)

    while running:
        screen.fill("green")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                map.process_click(mouse_pos, weapon_group, foundation_group, missile_group)

        map.render(screen)
        enemy_group.draw(screen)
        health_bar_group.draw(screen)
        missile_group.update(enemy_group)
        missile_group.draw(screen)
        weapon_group.update(screen, enemy_group)
        foundation_group.draw(screen)
        weapon_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()

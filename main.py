import pygame
import os
import sys
import pygame_gui
import pytmx
import sqlite3
from threading import Timer
from random import randint


all_sprites = pygame.sprite.Group()
floor_group = pygame.sprite.Group()
border_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bonus_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
clock = pygame.time.Clock()


class Gui:
    def __init__(self, manager):
        self.start_b = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 250), (100, 30)),
            text='start',
            manager=manager
        )
        self.options_b = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 290), (100, 30)),
            text='options',
            manager=manager
        )
        self.quit_b = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 330), (100, 30)),
            text='quit',
            manager=manager,
        )
        self.resume_b = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 250), (100, 30)),
            text='resume',
            manager=manager,
        )
        self.resume_b.hide()

    def hide_all(self):
        self.quit_b.hide()
        self.resume_b.hide()
        self.options_b.hide()

    def show_all(self):
        self.quit_b.show()
        self.resume_b.show()
        self.options_b.show()


class Welcome:
    def __init__(self, screen):
        screen.blit(load_image('приветственная.png'), (0, 0))


class Loading:
    def __init__(self, screen, mp):
        self.screen = screen
        self.n = 1
        self.change_photo()
        self.mp = mp
        self.f = False

    def change_photo(self):
        if self.n < 9:
            self.screen.blit(load_image(f'загрузка{self.n}.png'), (0, 0))
            self.n += 1
            self.timer = Timer(0.1, self.change_photo)
            self.timer.start()
        else:
            self.timer.cancel()
            self.mp.render()
            self.f = True


class Map:
    def __init__(self, filename, free_tiles, bonus_tiles, door_tiles, hero_tile, wall_tile):
        self.map = pytmx.load_pygame(f'уровни/{filename}')
        self.width = self.map.width
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tiles
        self.bonus_tiles = bonus_tiles
        self.door_tiles = door_tiles
        self.hero_tile = hero_tile
        self.wall_tile = wall_tile
        self.player_im = self.map.get_tile_image(0, 0, 1)
        self.player = None

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                floor = self.map.get_tile_image(x, y, 0)
                if floor:
                    Floor(x, y, floor)
                border = self.map.get_tile_image(x, y, 1)
                if border:
                    Border(x, y, border)
                bonus = self.map.get_tile_image(x, y, 2)
                if bonus:
                    Bonus(x, y, bonus)
                p1 = self.map.get_tile_image(x, y, 3)
                if p1:
                    self.player = Player(5, 5, p1)
                    self.p1 = p1
                p2 = self.map.get_tile_image(x, y, 4)
                if p2:
                    self.p2 = p2
                p3 = self.map.get_tile_image(x, y, 5)
                if p3:
                    self.p3 = p3
                p4 = self.map.get_tile_image(x, y, 6)
                if p4:
                    self.p4 = p4

    def get_tile_id(self, x, y, z):
        try:
            return self.map.tiledgidmap[self.map.get_tile_gid(x, y, z)]
        except:
            return -1

    def is_free(self, x, y):
        return self.get_tile_id(x, y, 1) != self.wall_tile

    def is_bonus(self, x, y):
        return self.get_tile_id(x, y, 2) in self.bonus_tiles


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, im):
        super().__init__(all_sprites, floor_group)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = x * 16
        self.rect.y = y * 16


class Border(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__(all_sprites, border_group)
        self.add(border_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * 16
        self.rect.y = y * 16


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, im):
        super().__init__(player_group, all_sprites)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = x * 16
        self.rect.y = y * 16
        self.health = 100
        self.velocity = 1
        self.armor = 0

    def update(self, x, y):
        self.rect = self.rect.move(x, y)

    def get_position_x(self):
        return int(-1 * (self.rect.x / 16) // 1 * -1)

    def get_position_y(self):
        return int(-1 * (self.rect.y / 16) // 1 * -1)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__(all_sprites, bonus_group)
        self.add(border_group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x * 16
        self.rect.y = y * 16


class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, size, image):
        super().__init__(all_sprites)
        self.add(door_group)
        self.image = image
        self.rect = size
        self.rect.x = x
        self.rect.y = y


def load_image(name, colorkey=None):
    fullname = os.path.join('data/moi', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def main():
    f = False
    is_menu = False
    is_main = False
    pygame.init()
    screen = pygame.display.set_mode((700, 552))
    pygame.display.set_caption('Chuck')
    manager = pygame_gui.UIManager((700, 552))
    Welcome(screen)
    gui = Gui(manager)
    clock = pygame.time.Clock()
    mp = Map('тест.tmx', 486, (901, 902, 933, 934),
             (718, 719, 720, 721, 750, 751, 752, 753), 1089, 418)
    run = True
    while run:
        time_delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                    rect=pygame.Rect((250, 200), (260, 200)),
                    manager=manager,
                    window_title='Подтверждение выхода',
                    action_long_desc='Вы уверены, что хотите выйти?',
                    action_short_name='Ok',
                    blocking=True
                )
            if event.type == pygame.KEYDOWN:
                if f:
                    if event.key == pygame.K_ESCAPE:
                        if is_menu:
                            gui.hide_all()
                            is_menu = False
                        else:
                            gui.show_all()
                            is_menu = True
                    if event.key == pygame.K_w and mp.is_free(mp.player.get_position_x(), mp.player.get_position_y() - 1):
                        mp.player.image = mp.p1
                        player_group.update(0, -1)
                    if event.key == pygame.K_s and mp.is_free(mp.player.get_position_x(), mp.player.get_position_y()):
                        mp.player.image = mp.p3
                        player_group.update(0, 1)
                    if event.key == pygame.K_a and mp.is_free(mp.player.get_position_x() - 1, mp.player.get_position_y()):
                        mp.player.image = mp.p4
                        player_group.update(-1, 0)
                    if event.key == pygame.K_d and mp.is_free(mp.player.get_position_x(), mp.player.get_position_y()):
                        mp.player.image = mp.p2
                        player_group.update(1, 0)


            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                run = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == gui.start_b:
                    load = Loading(screen, mp)
                    f = True
                    gui.start_b.hide()
                    gui.quit_b.hide()
                    gui.options_b.hide()

                if event.ui_element == gui.quit_b:
                    confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                        rect=pygame.Rect((250, 200), (260, 200)),
                        manager=manager,
                        window_title='Подтверждение выхода',
                        action_long_desc='Вы уверены, что хотите выйти?',
                        action_short_name='Ok',
                        blocking=True
                    )
                if event.ui_element == gui.options_b:
                    pass
                if event.ui_element == gui.resume_b:
                    pass
            manager.process_events(event)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and not keys[pygame.K_a] and not keys[pygame.K_d]\
                and not keys[pygame.K_s] and mp.is_free(mp.player.get_position_x(), mp.player.get_position_y() - 1):
            player_group.update(0, -1)
        if keys[pygame.K_s] and not keys[pygame.K_w] and not keys[pygame.K_d]\
                and not keys[pygame.K_a] and mp.is_free(mp.player.get_position_x(), mp.player.get_position_y()):
            player_group.update(0, 1)
        if keys[pygame.K_a] and not keys[pygame.K_w] and not keys[pygame.K_d]\
                and not keys[pygame.K_s] and mp.is_free(mp.player.get_position_x() - 1, mp.player.get_position_y()):
            player_group.update(-1, 0)
        if keys[pygame.K_d] and not keys[pygame.K_w] and not keys[pygame.K_a]\
                and not keys[pygame.K_s] and mp.is_free(mp.player.get_position_x(), mp.player.get_position_y()):
            player_group.update(1, 0)
        if f:
            if load.f:
                all_sprites.draw(screen)
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == '__main__':
    main()

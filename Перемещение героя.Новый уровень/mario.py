import pygame
import os
import sys


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is None:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = '300, 130'
pygame.display.set_caption('Перемещение героя. Камера')
screen_size = (500, 500)
width = 500
height = 500
screen = pygame.display.set_mode(screen_size)
FPS = 60
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Перемещение героя", "",
                  "Зацикливающийся уровень"]
    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 40)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 20
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')}
player_image = load_image('mario.png')
tile_width = tile_height = 50


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, side):
        global level_map
        if side == 'up':
            max_l_y = max(self, key=lambda sprite: sprite.abs_pos[1]).abs_pos[1]
            for sprite in self:
                sprite.abs_pos[1] -= (tile_height * max_y if sprite.abs_pos[1] == max_l_y else 0)
        elif side == 'down':
            min_l_y = min(self, key=lambda sprite: sprite.abs_pos[1]).abs_pos[1]
            for sprite in self:
                sprite.abs_pos[1] += (tile_height * max_y if sprite.abs_pos[1] == min_l_y else 0)
        elif side == 'left':
            max_l_x = max(self, key=lambda sprite: sprite.abs_pos[0]).abs_pos[0]
            for sprite in self:
                if sprite.abs_pos[0] == max_l_x:
                    sprite.abs_pos[0] -= tile_width * max_x
        elif side == 'right':
            min_l_x = min(self, key=lambda sprite: sprite.abs_pos[0]).abs_pos[0]
            for sprite in self:
                sprite.abs_pos[0] += (tile_height * max_x if sprite.abs_pos[0] == min_l_x else 0)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]

    def set_pos(self, x, y):
        self.abs_pos = [x, y]


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


player = None
sprite_group = SpriteGroup()
hero_group = SpriteGroup()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        y1 = y - 1 if y != 0 else max_y
        if level_map[y1][x] == '.':
            if y1 == max_y:
                for i in range(max_y - 1):
                    sprite_group.get_event('down')
                hero.move(x, y1 - 1)
            else:
                sprite_group.get_event('up')
                hero.move(x, y1)
    elif movement == "down":
        y1 = y + 1 if y != max_y else 0
        if level_map[y1][x] == '.':
            if y1 == 0:
                for i in range(max_y - 1):
                    sprite_group.get_event('up')
                hero.move(x, y1 + 1)
            else:
                sprite_group.get_event('down')
                hero.move(x, y1)
    elif movement == "left":
        x1 = x - 1 if x != 0 else max_x
        if level_map[y][x1] == '.':
            if x1 == max_x:
                for i in range(max_x - 1):
                    sprite_group.get_event('right')
                hero.move(x1 - 1, y)
            else:
                sprite_group.get_event('left')
                hero.move(x1, y)
    elif movement == "right":
        x1 = x + 1 if x != max_x else 0
        if level_map[y][x1] == '.':
            if x1 == 0:
                for i in range(max_x - 1):
                    sprite_group.get_event('left')
                hero.move(x1 + 1, y)
            else:
                sprite_group.get_event('right')
                hero.move(x1, y)


start_screen()
level_map = load_level("level.txt")
hero, max_x, max_y = generate_level(level_map)
camera = Camera()
camera.update(hero)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, "up")
            elif event.key == pygame.K_DOWN:
                move(hero, "down")
            elif event.key == pygame.K_LEFT:
                move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                move(hero, "right")
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    hero_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()

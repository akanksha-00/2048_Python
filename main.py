import pygame
import random
import math

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800, 800
ROWS = 4
COLUMNS = 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLUMNS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Game")

FONT = pygame.font.SysFont("comicsans", 60)
MOVE_VEL = 20


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(
        self,
        ceil=False,
    ):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLUMNS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)
    pygame.display.update()


def move_tiles(window, tiles, direction, clock):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda tile: tile.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        bounday_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL + RECT_WIDTH
        )
        ceil = True
    elif direction == "right":
        sort_func = lambda tile: tile.col
        reverse = True
        delta = (MOVE_VEL, 0)
        bounday_check = lambda tile: tile.col == COLUMNS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x + MOVE_VEL < next_tile.x
        move_check = (
            lambda tile, next_tile: tile.x + MOVE_VEL + RECT_WIDTH < next_tile.x
        )
        ceil = False
    elif direction == "down":
        sort_func = lambda tile: tile.row
        reverse = True
        delta = (0, MOVE_VEL)
        bounday_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y + MOVE_VEL < next_tile.y
        move_check = (
            lambda tile, next_tile: tile.y + MOVE_VEL + RECT_HEIGHT < next_tile.y
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda tile: tile.row
        reverse = False
        delta = (0, -MOVE_VEL)
        bounday_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL + RECT_HEIGHT
        )
        ceil = True

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if bounday_check(tile):
                continue

            next_tile = get_next_tile(tile)

            if not next_tile:
                tile.move(delta)
            elif (
                next_tile.value == tile.value
                and next_tile not in blocks
                and tile not in blocks
            ):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)

    return end_tiles(tiles)


def end_tiles(tiles):
    if len(tiles) == 16:
        return "lost"

    row, col = generate_random_tile(tiles)
    tiles[f"{row}{col}"] = Tile(2, row, col)

    return "continue"


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    draw(window, tiles)


def generate_random_tile(tiles):
    row = None
    column = None

    while True:
        row = random.randrange(0, ROWS)
        column = random.randrange(0, COLUMNS)
        if f"{row}{column}" not in tiles:
            break

    return row, column


def generate_tiles():
    tiles = {}

    for _ in range(2):
        row, column = generate_random_tile(tiles)
        tiles[f"{row}{column}"] = Tile(2, row, column)

    return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    result = move_tiles(window, tiles, "left", clock)
                elif event.key == pygame.K_RIGHT:
                    result = move_tiles(window, tiles, "right", clock)
                elif event.key == pygame.K_DOWN:
                    result = move_tiles(window, tiles, "down", clock)
                elif event.key == pygame.K_UP:
                    result = move_tiles(window, tiles, "up", clock)

        draw(window, tiles)

    pygame.quit()


if __name__ == "__main__":
    main(WINDOW)

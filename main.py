import asyncio
import curses
import random
import time
from itertools import cycle

from curses_tools import draw_frame, get_frame_size, read_controls

BORDER_SIZE = 1
TIC_TIMEOUT = 0.1
REPEAT_COEF = 2
MAX_STARS = 150
SHIP_SPEED = 10


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol="*"):
    while True:
        delay = random.randint(1, 5)
        await sleep(delay)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)
        canvas.addstr(row, column, symbol)
        await sleep(3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)
        canvas.addstr(row, column, symbol)
        await sleep(3)


def generage_stars(canvas):
    max_row, max_column = canvas.getmaxyx()
    stars = []
    for _ in range(MAX_STARS):
        pos_x = random.randint(BORDER_SIZE, max_column - BORDER_SIZE - 1)
        pos_y = random.randint(BORDER_SIZE, max_row - BORDER_SIZE - 1)
        symbol = random.choice("+*.:")
        stars.append(blink(canvas, pos_y, pos_x, symbol))
    return stars


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


def get_frame(path):
    with open(path, "r") as file:
        return file.read()


async def animate_spaceship(canvas, frames):
    frame_height, frame_width = get_frame_size(frames[0])
    max_row, max_column = canvas.getmaxyx()
    row = max_row // 2
    column = max_column // 2
    for frame in cycle(frames):
        draw_frame(canvas, row, column, frame)
        await sleep(1)
        row_offset, column_offset, space_pressed = read_controls(canvas)
        row_offset *= SHIP_SPEED
        column_offset *= SHIP_SPEED
        draw_frame(canvas, row, column, frame, negative=True)
        row = (
            min(row + row_offset, max_row - frame_height - BORDER_SIZE)
            if row_offset >= 0
            else max(row + row_offset, BORDER_SIZE)
        )
        column = (
            min(column + column_offset, max_column - frame_width - BORDER_SIZE)
            if column_offset > 0
            else max(column + column_offset, BORDER_SIZE)
        )


def draw(canvas):
    frames = [
        get_frame("./frames/rocket_frame_1.txt"),
        get_frame("./frames/rocket_frame_2.txt"),
    ]
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    coroutines = []
    coroutines.extend(generage_stars(canvas))
    # coroutines.append(fire(canvas, max_row-2, max_column//2))
    coroutines.append(animate_spaceship(canvas, frames))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        time.sleep(TIC_TIMEOUT)
        canvas.refresh()


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == "__main__":
    main()

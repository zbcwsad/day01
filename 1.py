import random
import tkinter as tk
from collections import deque
from dataclasses import dataclass


CELL_SIZE = 24
BOARD_WIDTH = 24
BOARD_HEIGHT = 20
TICK_MS = 120

BG_COLOR = "#101820"
GRID_COLOR = "#1d2b36"
SNAKE_HEAD_COLOR = "#50fa7b"
SNAKE_BODY_COLOR = "#2fd36b"
FOOD_COLOR = "#ff5555"
TEXT_COLOR = "#f8f8f2"

DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
    "W": (0, -1),
    "S": (0, 1),
    "A": (-1, 0),
    "D": (1, 0),
}


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def move(self, direction):
        dx, dy = direction
        return Point(self.x + dx, self.y + dy)


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)

        width = BOARD_WIDTH * CELL_SIZE
        height = BOARD_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.info = tk.Label(
            root,
            text="Arrow keys/WASD: move    Space: pause    R: restart",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 12),
            pady=8,
        )
        self.info.pack(fill="x")

        self.root.bind("<KeyPress>", self.on_key_press)
        self.after_id = None
        self.reset()

    def reset(self):
        start = Point(BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
        self.snake = deque(
            [
                start,
                Point(start.x - 1, start.y),
                Point(start.x - 2, start.y),
            ]
        )
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.paused = False
        self.game_over = False
        self.won = False
        self.food = self.spawn_food()

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.draw()
        self.schedule_tick()

    def spawn_food(self):
        snake_cells = set(self.snake)
        empty_cells = [
            Point(x, y)
            for x in range(BOARD_WIDTH)
            for y in range(BOARD_HEIGHT)
            if Point(x, y) not in snake_cells
        ]
        if not empty_cells:
            return None
        return random.choice(empty_cells)

    def on_key_press(self, event):
        key = event.keysym

        if key == "space":
            self.paused = not self.paused
            self.draw()
            return

        if key in {"r", "R"}:
            self.reset()
            return

        if key not in DIRECTIONS or self.game_over:
            return

        new_direction = DIRECTIONS[key]
        if not self.is_opposite(new_direction, self.direction):
            self.next_direction = new_direction

    @staticmethod
    def is_opposite(first, second):
        return first[0] + second[0] == 0 and first[1] + second[1] == 0

    def schedule_tick(self):
        self.after_id = self.root.after(TICK_MS, self.tick)

    def tick(self):
        if not self.paused and not self.game_over:
            self.direction = self.next_direction
            new_head = self.snake[0].move(self.direction)
            will_eat = new_head == self.food

            if self.hit_wall(new_head) or self.hit_self(new_head, will_eat):
                self.game_over = True
            else:
                self.snake.appendleft(new_head)
                if will_eat:
                    self.score += 1
                    self.food = self.spawn_food()
                    if self.food is None:
                        self.won = True
                        self.game_over = True
                else:
                    self.snake.pop()

        self.draw()
        self.schedule_tick()

    @staticmethod
    def hit_wall(point):
        return (
            point.x < 0
            or point.x >= BOARD_WIDTH
            or point.y < 0
            or point.y >= BOARD_HEIGHT
        )

    def hit_self(self, point, will_eat):
        body = self.snake if will_eat else list(self.snake)[:-1]
        return point in body

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_score()

        if self.paused:
            self.draw_center_text("Paused")
        elif self.won:
            self.draw_center_text("You Win!\nPress R to restart")
        elif self.game_over:
            self.draw_center_text("Game Over\nPress R to restart")

    def draw_grid(self):
        width = BOARD_WIDTH * CELL_SIZE
        height = BOARD_HEIGHT * CELL_SIZE

        for x in range(0, width, CELL_SIZE):
            self.canvas.create_line(x, 0, x, height, fill=GRID_COLOR)
        for y in range(0, height, CELL_SIZE):
            self.canvas.create_line(0, y, width, y, fill=GRID_COLOR)

    def draw_food(self):
        if self.food is None:
            return
        self.draw_cell(self.food, FOOD_COLOR)

    def draw_snake(self):
        for index, point in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
            self.draw_cell(point, color)

    def draw_cell(self, point, color):
        padding = 2
        x1 = point.x * CELL_SIZE + padding
        y1 = point.y * CELL_SIZE + padding
        x2 = (point.x + 1) * CELL_SIZE - padding
        y2 = (point.y + 1) * CELL_SIZE - padding
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw_score(self):
        self.canvas.create_text(
            12,
            12,
            text=f"Score: {self.score}",
            fill=TEXT_COLOR,
            anchor="nw",
            font=("Arial", 16, "bold"),
        )

    def draw_center_text(self, text):
        width = BOARD_WIDTH * CELL_SIZE
        height = BOARD_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(
            0,
            height // 2 - 60,
            width,
            height // 2 + 60,
            fill="#000000",
            stipple="gray50",
            outline="",
        )
        self.canvas.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=TEXT_COLOR,
            font=("Arial", 28, "bold"),
            justify="center",
        )


def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

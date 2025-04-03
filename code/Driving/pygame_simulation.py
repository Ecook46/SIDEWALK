import pygame
import sys

# --- CONFIGURATIONS ---
GRID_ROWS = 10
GRID_COLS = 10
CELL_SIZE = 80
BATTERY_LIMIT = 40  # This remains fixed and is displayed

# Colors (R, G, B)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
VISITED_COLOR = (173, 216, 230)  # Light blue for visited cells

# Initialize pygame
pygame.init()

# Calculate window size
WINDOW_WIDTH = GRID_COLS * CELL_SIZE
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Car Parking Lot Simulation")

# Load and scale the car image
try:
    car_image = pygame.image.load("car.jpeg")
except pygame.error:
    print("Could not load car.jpeg. Please place a car.jpeg file in this directory.")
    sys.exit()

car_image = pygame.transform.scale(car_image, (CELL_SIZE - 10, CELL_SIZE - 10))

# Clock for controlling FPS
clock = pygame.time.Clock()
FPS = 5

# --- GAME STATE ---

# The car starts at (row=0, col=0)
car_row = 0
car_col = 0
# Battery remains constant; we simulate consumption with "consumed_steps"
consumed_steps = 0

# Mark visited cells (initialize grid of booleans)
visited = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
visited[car_row][car_col] = True

# We store the snake-like path in a list of (row, col) cells:
snake_path = []
for r in range(GRID_ROWS):
    if r % 2 == 0:  # Even row: left to right
        for c in range(GRID_COLS):
            snake_path.append((r, c))
    else:           # Odd row: right to left
        for c in range(GRID_COLS - 1, -1, -1):
            snake_path.append((r, c))

# Index to track where we are on the snake path
path_index = 0

def steps_to_return_home(row, col):
    """
    Returns the minimal steps to get from (row, col) back to (0, 0),
    given the rule: go straight up to row=0, then go left to col=0.
    """
    return row + col

def compute_return_path(row, col):
    """
    Returns a list of grid cells that lead from (row, col) to home (0,0)
    by moving vertically upward until row==0, then horizontally left.
    """
    path = []
    current_row, current_col = row, col
    # Move up until we reach row 0
    while current_row > 0:
        current_row -= 1
        path.append((current_row, current_col))
    # Move left until we reach col 0
    while current_col > 0:
        current_col -= 1
        path.append((current_row, current_col))
    return path

def draw_grid():
    """
    Draw the grid with visited cells colored differently.
    """
    screen.fill(GRAY)
    # Fill in visited cells
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if visited[r][c]:
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, VISITED_COLOR, rect)
    # Draw grid lines
    for r in range(GRID_ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, r * CELL_SIZE), (WINDOW_WIDTH, r * CELL_SIZE), 2)
    for c in range(GRID_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * CELL_SIZE, 0), (c * CELL_SIZE, WINDOW_HEIGHT), 2)

def draw_car(row, col):
    """
    Draw the car image at grid cell (row, col).
    """
    x = col * CELL_SIZE + 5
    y = row * CELL_SIZE + 5
    screen.blit(car_image, (x, y))

# --- STATE VARIABLES for battery return routine ---
state = "exploring"  # can be "exploring", "returning_home", "returning_to_explore"
# Variables to store the exploration state when emergency return is triggered:
saved_position = None
saved_index = None
# For tracking the return journey:
return_path = []
return_index = 0
# For tracking the reverse journey (back to saved exploration position):
explore_return_path = []
explore_return_index = 0

# --- MAIN LOOP ---
running = True
while running:
    clock.tick(FPS)
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if state == "exploring":
        if path_index >= len(snake_path):
            # Finished exploring all cells.
            running = False
        else:
            # Peek at the next cell
            next_row, next_col = snake_path[path_index]
            # Check if after making the move the remaining capacity (BATTERY_LIMIT - consumed_steps)
            # would be insufficient to return home.
            if (BATTERY_LIMIT - consumed_steps - 1) < steps_to_return_home(next_row, next_col):
                # Not enough effective battery to safely return if we move to the next cell:
                # Initiate emergency return routine:
                saved_position = (car_row, car_col)
                saved_index = path_index
                return_path = compute_return_path(car_row, car_col)
                return_index = 0
                state = "returning_home"
            else:
                # Normal move along the snake path:
                car_row, car_col = next_row, next_col
                visited[car_row][car_col] = True
                path_index += 1
                consumed_steps += 1

    elif state == "returning_home":
        # Follow the computed return path to get to home.
        if return_index < len(return_path):
            car_row, car_col = return_path[return_index]
            visited[car_row][car_col] = True
            consumed_steps += 1  # Simulate battery consumption during return.
            return_index += 1
        else:
            # Arrived at home. Recharge (reset consumed_steps).
            consumed_steps = 0
            # Prepare to return to the saved exploration position by reversing the return path.
            explore_return_path = return_path[::-1]
            explore_return_index = 0
            state = "returning_to_explore"

    elif state == "returning_to_explore":
        # Follow the reverse of the return path back to the last exploration cell.
        if explore_return_index < len(explore_return_path):
            car_row, car_col = explore_return_path[explore_return_index]
            visited[car_row][car_col] = True
            consumed_steps += 1  # Now count the retracing steps as well.
            explore_return_index += 1
        else:
            # Now back to the saved exploration position; resume exploring.
            state = "exploring"

    # --- RENDERING ---
    draw_grid()
    draw_car(car_row, car_col)

    # Display battery (always fixed), consumed steps, and steps needed to return home on the screen.
    font = pygame.font.SysFont(None, 30)
    status_text = (
        f"Battery: {BATTERY_LIMIT} | Consumed: {consumed_steps} | "
        f"Steps to return: {steps_to_return_home(car_row, car_col)} | State: {state}"
    )
    text_surface = font.render(status_text, True, GREEN)
    screen.blit(text_surface, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()


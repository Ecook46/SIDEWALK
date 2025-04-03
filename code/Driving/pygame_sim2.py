import pygame
import sys

# --- CONFIGURATIONS ---
GRID_ROWS = 10
GRID_COLS = 10
CELL_SIZE = 80
BATTERY_LIMIT = 40  # Battery remains fixed (displayed value)

# Colors (R, G, B)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
VISITED_COLOR = (173, 216, 230)  # Light blue for visited cells
OBSTACLE_COLOR = (255, 0, 0)       # Red for obstacles

# Preset obstacles (spread out, not clumped)
obstacles = [(2, 5), (4, 7), (6, 3), (7, 1), (8, 8)]

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
car_row = 0
car_col = 0
# consumed_steps simulates battery consumption; displayed battery remains fixed
consumed_steps = 0

# Grid to track visited cells
visited = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
visited[car_row][car_col] = True

# Generate snake-like exploration path.
snake_path = []
for r in range(GRID_ROWS):
    if r % 2 == 0:  # Even row: left to right.
        for c in range(GRID_COLS):
            snake_path.append((r, c))
    else:           # Odd row: right to left.
        for c in range(GRID_COLS - 1, -1, -1):
            snake_path.append((r, c))
path_index = 0

def steps_to_return_home(row, col):
    """
    Returns the minimal steps to get from (row, col) back to (0, 0)
    by moving vertically upward and then horizontally.
    """
    return row + col

def compute_return_path_avoiding_obstacles(row, col):
    """
    Returns a list of grid cells leading from (row, col) to home (0,0)
    by moving upward then left. If a move is blocked by an obstacle,
    a simple detour (horizontal or vertical) is attempted.
    """
    path = []
    current_row, current_col = row, col
    # Move upward until row 0 is reached.
    while current_row > 0:
        if (current_row - 1, current_col) not in obstacles:
            current_row -= 1
            path.append((current_row, current_col))
        else:
            # Obstacle above; try a horizontal detour.
            if current_col + 1 < GRID_COLS and ((current_row, current_col + 1) not in obstacles):
                current_col += 1
                path.append((current_row, current_col))
            elif current_col - 1 >= 0 and ((current_row, current_col - 1) not in obstacles):
                current_col -= 1
                path.append((current_row, current_col))
            else:
                break
    # Then move left until col 0 is reached.
    while current_col > 0:
        if (current_row, current_col - 1) not in obstacles:
            current_col -= 1
            path.append((current_row, current_col))
        else:
            # Obstacle to the left; try a vertical detour.
            if current_row > 0 and ((current_row - 1, current_col) not in obstacles):
                current_row -= 1
                path.append((current_row, current_col))
            elif current_row < GRID_ROWS - 1 and ((current_row + 1, current_col) not in obstacles):
                current_row += 1
                path.append((current_row, current_col))
            else:
                break
    return path

def compute_exploration_detour(current, next_cell):
    """
    Returns a fixed detour route from the current cell to a cell
    two horizontal moves away. The detour is:
      1. Vertical down one cell.
      2. Horizontal move (in the same direction as from current to next_cell).
      3. Another horizontal move.
      4. Vertical up one cell.
    This returns the list of cells for the detour.
    """
    (r, c) = current
    # Determine horizontal direction from current cell to next_cell.
    step = 1 if next_cell[1] > c else -1
    route = []
    # Move vertically down 1 cell.
    new_r = r + 1 if r + 1 < GRID_ROWS else r - 1
    route.append((new_r, c))
    # Two horizontal moves.
    new_c = c + step
    route.append((new_r, new_c))
    new_c += step
    route.append((new_r, new_c))
    # Move vertically up 1 cell to return to original row.
    route.append((r, new_c))
    return route

def draw_grid():
    """
    Draws the grid along with visited cells and obstacles.
    """
    screen.fill(GRAY)
    # Draw visited cells.
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if visited[r][c]:
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, VISITED_COLOR, rect)
    # Draw obstacles.
    for (r, c) in obstacles:
        rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, OBSTACLE_COLOR, rect)
    # Draw grid lines.
    for r in range(GRID_ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, r * CELL_SIZE), (WINDOW_WIDTH, r * CELL_SIZE), 2)
    for c in range(GRID_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * CELL_SIZE, 0), (c * CELL_SIZE, WINDOW_HEIGHT), 2)

def draw_car(row, col):
    """
    Draws the car image at grid cell (row, col).
    """
    x = col * CELL_SIZE + 5
    y = row * CELL_SIZE + 5
    screen.blit(car_image, (x, y))

# --- STATE VARIABLES for battery return routine ---
state = "exploring"  # Other states: "returning_home", "returning_to_explore"
saved_position = None   # Last exploration position before emergency return.
saved_index = None      # snake_path index saved for resuming exploration.
return_path = []        # Path computed for returning home.
return_index = 0        # Index for traversing the return path.
explore_return_path = []  # Reverse of return_path to return to exploring.
explore_return_index = 0

# For managing exploration detours.
detour_path = []      # List of cells in the current detour route.

# --- MAIN LOOP ---
running = True
while running:
    clock.tick(FPS)
    # Process events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if state == "exploring":
        if detour_path:
            # Follow the detour route if one is in progress.
            # Use the final cell of the detour (target) for battery check.
            final_detour_cell = detour_path[-1]
            if (BATTERY_LIMIT - consumed_steps - 1) < steps_to_return_home(final_detour_cell[0], final_detour_cell[1]):
                # Not enough battery: initiate emergency return.
                saved_position = (car_row, car_col)
                saved_index = path_index
                return_path = compute_return_path_avoiding_obstacles(car_row, car_col)
                return_index = 0
                state = "returning_home"
            else:
                next_detour = detour_path.pop(0)
                car_row, car_col = next_detour
                visited[car_row][car_col] = True
                consumed_steps += 1
                # If detour is complete, continue with normal exploration.
                if not detour_path:
                    # We assume the detour landed on a cell that is two cells ahead on snake_path.
                    path_index += 2
        else:
            # No detour in progress; follow the snake_path.
            if path_index >= len(snake_path):
                running = False
            else:
                target = snake_path[path_index]
                # If the next target is an obstacle, compute a detour.
                if target in obstacles:
                    # Compute a fixed detour route.
                    detour_path = compute_exploration_detour((car_row, car_col), target)
                    # Do not update path_index yet; it will be updated after completing the detour.
                    continue
                # Battery check using the target cell.
                if (BATTERY_LIMIT - consumed_steps - 1) < steps_to_return_home(target[0], target[1]):
                    saved_position = (car_row, car_col)
                    saved_index = path_index
                    return_path = compute_return_path_avoiding_obstacles(car_row, car_col)
                    return_index = 0
                    state = "returning_home"
                else:
                    # Move directly to the target cell.
                    car_row, car_col = target
                    visited[car_row][car_col] = True
                    path_index += 1
                    consumed_steps += 1

    elif state == "returning_home":
        if return_index < len(return_path):
            car_row, car_col = return_path[return_index]
            visited[car_row][car_col] = True
            consumed_steps += 1
            return_index += 1
        else:
            # Arrived at home; recharge battery.
            consumed_steps = 0
            explore_return_path = return_path[::-1]
            explore_return_index = 0
            state = "returning_to_explore"

    elif state == "returning_to_explore":
        if explore_return_index < len(explore_return_path):
            car_row, car_col = explore_return_path[explore_return_index]
            visited[car_row][car_col] = True
            consumed_steps += 1
            explore_return_index += 1
        else:
            state = "exploring"

    # --- RENDERING ---
    draw_grid()
    draw_car(car_row, car_col)
    font = pygame.font.SysFont(None, 30)
    status_text = (f"Battery: {BATTERY_LIMIT} | Consumed: {consumed_steps} | "
                   f"Steps to return: {steps_to_return_home(car_row, car_col)} | State: {state}")
    text_surface = font.render(status_text, True, GREEN)
    screen.blit(text_surface, (10, 10))
    pygame.display.flip()

pygame.quit()
sys.exit()

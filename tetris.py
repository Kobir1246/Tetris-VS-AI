# competitive_tetris.py
# Competitive Tetris: Player vs AI with welcome menu + player-only Next preview
# Requires: pygame

import pygame, random, copy, sys, time, math

# ----------------------
# CONFIG (logical canvas)
# ----------------------
TILE = 28
ROWS, COLS = 20, 10
LEFT_OFFSET = 40
RIGHT_OFFSET = LEFT_OFFSET + COLS * TILE + 80  # 80px gap in the middle (used for "Next")
SCREEN_W = RIGHT_OFFSET + COLS * TILE + LEFT_OFFSET
SCREEN_H = ROWS * TILE + 80

FPS = 60

# initial fall speeds (milliseconds per drop)
PLAYER_BASE_SPEED = 450      # overwritten by welcome selection
AI_BASE_SPEED = 420

# difficulty manager thresholds (unchanged)
SPEED_STEP = 50
DIFF_STEP = 500
POWER_JUMP = 300
POWER_JUMP_THRESHOLD = 1000
POWER_JUMP_DURATION = 8.0

# AI parameters (unchanged)
AI_MISTAKE_CHANCE = {
    'easy': 0.30,
    'medium': 0.12,
    'hard': 0.06
}

# colors
BLACK = (0, 0, 0)
GRAY = (70, 70, 70)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128),
    (255, 0, 0)
]
GHOST = (140, 140, 140)

# tetromino shapes (as matrices)
SHAPES = [
    [[1,1,1,1]],                # I
    [[1,1],[1,1]],              # O
    [[0,1,0],[1,1,1]],          # T
    [[1,0,0],[1,1,1]],          # J
    [[0,0,1],[1,1,1]],          # L
    [[1,1,0],[0,1,1]],          # S
    [[0,1,1],[1,1,0]]           # Z
]

# ----------------------
# Pygame init & fonts
# ----------------------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
window_w, window_h = screen.get_size()
pygame.display.set_caption("Competitive Tetris")
game_surface = pygame.Surface((SCREEN_W, SCREEN_H))  # logical canvas

font_big = pygame.font.SysFont("comicsans", 60, bold=True)
font_small = pygame.font.SysFont("comicsans", 30, bold=True)
font = pygame.font.SysFont(None, 26)
big_font = pygame.font.SysFont(None, 48)

clock = pygame.time.Clock()

# ----------------------
# Welcome / difficulty selection
# ----------------------
def welcome_screen(game_surface):
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 64, bold=True)
    font_small = pygame.font.SysFont("Arial", 28)

    title = "TETRIS vs AI"
    difficulties = ["Easy", "Medium", "Hard"]
    selected_idx = 0
    press_text = "Press SPACE to start"

    frame = 0
    waiting = True
    while waiting:
        # draw to logical canvas
        game_surface.fill((30, 30, 60))  # dark blue background

        # Neon gradient colors (cycle every frame)
        colors = [(255, 100, 150), (100, 200, 255), (150, 255, 150)]
        color = colors[(frame // 20) % len(colors)]

        # Bounce offset
        bounce = int(20 * math.sin(frame * 0.08))

        # Title text with bounce
        text_surface = font_big.render(title, True, color)
        rect = text_surface.get_rect(center=(SCREEN_W // 2, SCREEN_H // 3 + bounce))
        game_surface.blit(text_surface, rect)

        # Difficulty options
        y_pos = SCREEN_H // 2
        for i, diff in enumerate(difficulties):
            col = (255, 255, 255)
            if i == selected_idx:
                col = (0, 255, 0)  # highlight
            diff_surface = font_small.render(diff, True, col)
            diff_rect = diff_surface.get_rect(center=(SCREEN_W // 2, y_pos + i * 40))
            game_surface.blit(diff_surface, diff_rect)

        # Instruction text
        instr_surface = font_small.render(press_text, True, (200, 200, 200))
        instr_rect = instr_surface.get_rect(center=(SCREEN_W // 2, SCREEN_H - 80))
        game_surface.blit(instr_surface, instr_rect)

        # scale/blit to fullscreen
        scale = min(window_w / SCREEN_W, window_h / SCREEN_H)
        scaled_surface = pygame.transform.smoothscale(
            game_surface, (int(SCREEN_W * scale), int(SCREEN_H * scale))
        )
        x = (window_w - scaled_surface.get_width()) // 2
        y = (window_h - scaled_surface.get_height()) // 2

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (x, y))
        pygame.display.flip()

        clock.tick(60)
        frame += 1

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return difficulties[selected_idx]  # return chosen difficulty
                elif event.key == pygame.K_LEFT:
                    selected_idx = (selected_idx - 1) % len(difficulties)
                elif event.key == pygame.K_RIGHT:
                    selected_idx = (selected_idx + 1) % len(difficulties)

# Map a chosen label to a player base speed (ms per drop)
def difficulty_to_player_speed(label):
    if label == "Easy":
        return 580
    if label == "Medium":
        return 450
    return 320  # Hard

# --- show welcome/difficulty once and set PLAYER_BASE_SPEED ---
PLAYER_DIFFICULTY = welcome_screen(game_surface)
PLAYER_BASE_SPEED = difficulty_to_player_speed(PLAYER_DIFFICULTY)
player_speed = PLAYER_BASE_SPEED  # initial current speed
ai_speed = AI_BASE_SPEED

# ----------------------
# Helper functions (unchanged)
# ----------------------
def create_empty_grid():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def rotate_shape(shape):
    # rotate clockwise
    return [list(row) for row in zip(*shape[::-1])]

def valid_position(tet, grid):
    """Return True if tetromino at tet.x, tet.y fits inside grid and not colliding."""
    for y, row in enumerate(tet.shape):
        for x, cell in enumerate(row):
            if cell:
                nx = tet.x + x
                ny = tet.y + y
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and grid[ny][nx]:
                    return False
    return True

def merge(tet, grid):
    """Write tet into grid safely (only inside bounds)."""
    for y, row in enumerate(tet.shape):
        for x, cell in enumerate(row):
            if cell:
                nx = tet.x + x
                ny = tet.y + y
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    grid[ny][nx] = tet.color_index

def clear_lines(grid):
    new = [row for row in grid if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new)
    for _ in range(cleared):
        new.insert(0, [0] * COLS)
    return new, cleared

def board_full(grid):
    """Return True if any cell in top row is occupied (board considered full)."""
    return any(cell != 0 for cell in grid[0])

# evaluation heuristic for AI (lower is better)
def evaluate_grid(temp):
    holes = 0
    heights = []
    aggregate_height = 0
    bumpiness = 0
    max_height = 0

    for x in range(COLS):
        col_h = 0
        block_found = False
        col_h_from_top = 0
        for y in range(ROWS):
            if temp[y][x]:
                if not block_found:
                    col_h_from_top = y
                    block_found = True
        if block_found:
            col_h = ROWS - col_h_from_top
        heights.append(col_h)
        aggregate_height += col_h
        max_height = max(max_height, col_h)

    # holes
    for x in range(COLS):
        filled = False
        for y in range(ROWS):
            if temp[y][x]:
                filled = True
            elif filled:
                holes += 1

    for i in range(COLS - 1):
        bumpiness += abs(heights[i] - heights[i+1])

    # tuned weights (holes are heavily penalized)
    score = holes * 6.0 + aggregate_height * 0.9 + bumpiness * 0.5 + max_height * 0.3
    return score

# ----------------------
# Tetromino class
# ----------------------
class Tetromino:
    def __init__(self, shape=None, color_idx=None):
        if shape is None:
            shape = random.choice(SHAPES)
        self.base_shape = copy.deepcopy(shape)   # keep base for rotations
        self.shape = copy.deepcopy(shape)
        self.color_index = color_idx if color_idx is not None else random.randint(1, len(COLORS))
        self.color = COLORS[self.color_index - 1]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = -len(self.shape)  # start above the grid
        self.rotation = 0

    def rotate(self):
        # rotate shape and track rotation mod 4
        self.shape = rotate_shape(self.shape)
        self.rotation = (self.rotation + 1) % 4

    def reset_from_base(self, r):
        # set to base shape rotated r times
        s = copy.deepcopy(self.base_shape)
        for _ in range(r % 4):
            s = rotate_shape(s)
        self.shape = s
        self.rotation = r % 4

# ----------------------
# AI planning (unchanged)
# ----------------------
def ai_plan_best(tet, grid, mistake_prob=0.12):
    best_score = float('inf')
    best_move = (tet.x, 0)  # fallback
    moves = []

    for r in range(4):
        tmp_shape = copy.deepcopy(tet.base_shape)
        for _ in range(r):
            tmp_shape = rotate_shape(tmp_shape)
        width = len(tmp_shape[0])
        for x in range(-2, COLS - width + 3):
            t = Tetromino(shape=tmp_shape, color_idx=tet.color_index)
            t.base_shape = copy.deepcopy(tmp_shape)
            t.shape = copy.deepcopy(tmp_shape)
            t.x = x
            t.y = 0
            while valid_position(t, grid):
                t.y += 1
            t.y -= 1
            if not valid_position(t, grid):
                continue
            temp = copy.deepcopy(grid)
            merge(t, temp)
            temp_after_clear, cleared = clear_lines(temp)
            score = evaluate_grid(temp_after_clear) - cleared * 4.5
            moves.append(((x, r), score))
            if score < best_score:
                best_score = score
                best_move = (x, r)

    if not moves:
        return tet.x, 0

    moves.sort(key=lambda s: s[1])
    if random.random() < mistake_prob and len(moves) > 1:
        idx = min(len(moves)-1, random.randint(1, min(3, len(moves)-1)))
        choice = moves[idx][0]
    else:
        choice = moves[0][0]
    return choice  # (target_x, target_rot)

# ----------------------
# Draw helpers
# ----------------------
def draw_board(grid, offset_x, title, score):
    # background
    pygame.draw.rect(game_surface, (30,30,30), (offset_x-10, 30, COLS*TILE+20, ROWS*TILE+20))
    # grid cells
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(offset_x + x*TILE, 40 + y*TILE, TILE-1, TILE-1)
            val = grid[y][x]
            if val:
                pygame.draw.rect(game_surface, COLORS[val-1], rect)
            else:
                pygame.draw.rect(game_surface, (45,45,45), rect)
    # title & score (draw to game_surface, not screen)
    txt = font.render(f"{title}  Score: {score}", True, WHITE)
    game_surface.blit(txt, (offset_x, 5))

def draw_tet_on_grid(tet, offset_x):
    for y, row in enumerate(tet.shape):
        for x, cell in enumerate(row):
            if cell:
                px = offset_x + (tet.x + x)*TILE
                py = 40 + (tet.y + y)*TILE
                rect = pygame.Rect(px, py, TILE-1, TILE-1)
                pygame.draw.rect(game_surface, tet.color, rect)
                pygame.draw.rect(game_surface, BLACK, rect, 1)

def draw_ghost(tet, grid, offset_x):
    ghost = Tetromino(shape=tet.shape, color_idx=tet.color_index)
    ghost.x = tet.x
    ghost.y = tet.y
    while valid_position(ghost, grid):
        ghost.y += 1
    ghost.y -= 1
    for y, row in enumerate(ghost.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(offset_x + (ghost.x + x)*TILE, 40 + (ghost.y + y)*TILE, TILE-1, TILE-1)
                pygame.draw.rect(game_surface, GHOST, rect)
                pygame.draw.rect(game_surface, BLACK, rect, 1)

# player next preview panel
def draw_player_next_preview(next_tet):
    box_x = LEFT_OFFSET + COLS*TILE + 8     # inside the 80px gap
    box_y = 80
    box_w = 64
    box_h = 100

    # panel
    pygame.draw.rect(game_surface, (28,28,32), (box_x-6, box_y-28, box_w+12, box_h+40), border_radius=8)
    pygame.draw.rect(game_surface, (60,60,66), (box_x-6, box_y-28, box_w+12, box_h+40), 2, border_radius=8)

    label = font.render("Next", True, WHITE)
    game_surface.blit(label, (box_x + (box_w - label.get_width())//2, box_y - 24))

    # scale piece to preview area
    preview_tile = 16
    shape_w = len(next_tet.shape[0]) * preview_tile
    shape_h = len(next_tet.shape) * preview_tile
    start_x = box_x + (box_w - shape_w)//2
    start_y = box_y + (box_h - shape_h)//2

    for y, row in enumerate(next_tet.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(start_x + x*preview_tile, start_y + y*preview_tile, preview_tile-1, preview_tile-1)
                pygame.draw.rect(game_surface, next_tet.color, rect)
                pygame.draw.rect(game_surface, BLACK, rect, 1)

# Wall-kick helper for player (unchanged)
def try_wall_kick(tet, grid):
    if valid_position(tet, grid):
        return True
    for dx in (1, -1, 2, -2):
        tet.x += dx
        if valid_position(tet, grid):
            return True
        tet.x -= dx
    return False

# ----------------------
# Game initialization & state
# ----------------------
player_grid = create_empty_grid()
ai_grid = create_empty_grid()
player_score = 0
ai_score = 0

# AI difficulty remains as you set before
DIFFICULTY = 'medium'
ai_mistake = AI_MISTAKE_CHANCE.get(DIFFICULTY, 0.12)

# Next-piece usage: create both current and next for player before starting loop
player_tet = Tetromino()
player_next_tet = Tetromino()
ai_tet = Tetromino()

ai_plan = {'target_x': ai_tet.x, 'target_rot': 0, 'planned': False}

# timers
player_timer = 0
ai_timer = 0
start_time = time.time()
diff_timer = 0.0

# power-jump trackers
last_power_time = 0
power_active = False
power_owner = None  # 'player' or 'ai'
power_end_time = 0

# winner state
running = True
winner = None

# ----------------------
# Difficulty manager (uses PLAYER_BASE_SPEED assigned from welcome screen)
# ----------------------
def difficulty_manager():
    global player_speed, ai_speed, player_score, ai_score, last_power_time, power_active, power_owner, power_end_time
    diff = player_score - ai_score
    # reset to base every tick (menu already set PLAYER_BASE_SPEED)
    player_speed = PLAYER_BASE_SPEED
    ai_speed = AI_BASE_SPEED

    # apply speed increases for leader
    if diff > DIFF_STEP:
        player_speed = max(120, PLAYER_BASE_SPEED - SPEED_STEP)
    if diff < -DIFF_STEP:
        ai_speed = max(120, AI_BASE_SPEED - SPEED_STEP)
    if diff > 2 * DIFF_STEP:
        player_speed = max(100, PLAYER_BASE_SPEED - 2 * SPEED_STEP)
    if diff < -2 * DIFF_STEP:
        ai_speed = max(100, AI_BASE_SPEED - 2 * SPEED_STEP)

    # power jump event (give trailing player a bonus)
    now = time.time()
    if (now - last_power_time) > 15:
        if diff >= POWER_JUMP_THRESHOLD:
            ai_score += POWER_JUMP
            power_active = True
            power_owner = 'ai'
            power_end_time = now + POWER_JUMP_DURATION
            last_power_time = now
        elif diff <= -POWER_JUMP_THRESHOLD:
            player_score += POWER_JUMP
            power_active = True
            power_owner = 'player'
            power_end_time = now + POWER_JUMP_DURATION
            last_power_time = now

    if power_active and now > power_end_time:
        power_active = False
        power_owner = None

# ----------------------
# Main loop
# ----------------------
while running:
    dt = clock.tick(FPS)
    player_timer += dt
    ai_timer += dt
    diff_timer += dt / 1000.0

    # quick top-row full check each frame
    if board_full(player_grid):
        winner = 'AI (Player board full)'
        running = False
    if board_full(ai_grid):
        winner = 'Player (AI board full)'
        running = False
    if not running:
        break

    # difficulty manager every second
    if diff_timer >= 1.0:
        diff_timer = 0.0
        difficulty_manager()

    # apply temporary slowdown if power active
    cur_player_speed = player_speed
    cur_ai_speed = ai_speed
    if power_active and power_owner == 'ai':
        cur_player_speed = min(1000, cur_player_speed + 220)
    if power_active and power_owner == 'player':
        cur_ai_speed = min(1000, cur_ai_speed + 220)

    # events
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                running = False
            elif ev.key == pygame.K_LEFT:
                player_tet.x -= 1
                if not valid_position(player_tet, player_grid):
                    player_tet.x += 1
            elif ev.key == pygame.K_RIGHT:
                player_tet.x += 1
                if not valid_position(player_tet, player_grid):
                    player_tet.x -= 1
            elif ev.key == pygame.K_UP:
                # rotate with simple wall kick
                player_tet.rotate()
                if not try_wall_kick(player_tet, player_grid):
                    for _ in range(3):
                        player_tet.rotate()
            elif ev.key == pygame.K_DOWN:
                # soft drop
                player_tet.y += 1
                if not valid_position(player_tet, player_grid):
                    player_tet.y -= 1

    # PLAYER drop
    if player_timer >= cur_player_speed:
        player_timer = 0
        player_tet.y += 1
        if not valid_position(player_tet, player_grid):
            player_tet.y -= 1
            # lock
            merge(player_tet, player_grid)
            player_grid, cleared = clear_lines(player_grid)
            player_score += cleared * 100

            # check board-full right after lock/clear
            if board_full(player_grid):
                winner = 'AI (Player board full)'
                running = False
                break

            # spawn from next, then produce a new next
            player_tet = player_next_tet
            player_next_tet = Tetromino()

            # top-out check
            if not valid_position(player_tet, player_grid):
                winner = 'AI (Player topped out)'
                running = False
                break

    # AI planning & execution
    if not ai_plan['planned']:
        tx, trot = ai_plan_best(ai_tet, ai_grid, mistake_prob=ai_mistake)
        ai_plan['target_x'] = tx
        ai_plan['target_rot'] = trot
        ai_plan['planned'] = True

    if ai_timer >= cur_ai_speed and running:
        ai_timer = 0
        if ai_plan['target_rot'] > 0:
            ai_tet.rotate()
            ai_plan['target_rot'] -= 1
            if not try_wall_kick(ai_tet, ai_grid):
                for _ in range(3):
                    ai_tet.rotate()
        else:
            if ai_tet.x < ai_plan['target_x']:
                ai_tet.x += 1
                if not valid_position(ai_tet, ai_grid):
                    ai_tet.x -= 1
            elif ai_tet.x > ai_plan['target_x']:
                ai_tet.x -= 1
                if not valid_position(ai_tet, ai_grid):
                    ai_tet.x += 1
            else:
                while valid_position(ai_tet, ai_grid):
                    ai_tet.y += 1
                ai_tet.y -= 1
                merge(ai_tet, ai_grid)
                ai_grid, cleared = clear_lines(ai_grid)
                ai_score += cleared * 100

                if board_full(ai_grid):
                    winner = 'Player (AI board full)'
                    running = False
                    break

                ai_tet = Tetromino()
                ai_plan['planned'] = False
                if not valid_position(ai_tet, ai_grid):
                    winner = 'Player (AI topped out)'
                    running = False
                    break

    # ----------------------
    # DRAW to logical canvas
    # ----------------------
    game_surface.fill((18,18,18))

    draw_board(player_grid, LEFT_OFFSET, "Player", player_score)
    draw_board(ai_grid, RIGHT_OFFSET, "AI", ai_score)

    # player's falling tetromino & ghost
    draw_ghost(player_tet, player_grid, LEFT_OFFSET)
    draw_tet_on_grid(player_tet, LEFT_OFFSET)

    # AI ghost preview
    ghost_planned = Tetromino(shape=ai_tet.base_shape, color_idx=ai_tet.color_index)
    ghost_planned.reset_from_base(0)
    ghost_planned.shape = copy.deepcopy(ai_tet.shape)
    ghost_planned.x = ai_plan.get('target_x', ai_tet.x)
    ghost_planned.y = ai_tet.y
    while valid_position(ghost_planned, ai_grid):
        ghost_planned.y += 1
    ghost_planned.y -= 1
    for y, row in enumerate(ghost_planned.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(RIGHT_OFFSET + (ghost_planned.x + x) * TILE,
                                   40 + (ghost_planned.y + y) * TILE, TILE-1, TILE-1)
                pygame.draw.rect(game_surface, GHOST, rect)
                pygame.draw.rect(game_surface, BLACK, rect, 1)

    # AI tetromino
    draw_tet_on_grid(ai_tet, RIGHT_OFFSET)

    # player's next preview
    draw_player_next_preview(player_next_tet)

    # HUD (show both: player difficulty from menu, and current AI difficulty tag)
    status = font.render(
        f"PlayerDiff: {PLAYER_DIFFICULTY.title()}   AIDiff: {DIFFICULTY.title()}   PowerActive: {power_active}   OwnerSlow: {power_owner}",
        True, WHITE)
    game_surface.blit(status, (10, SCREEN_H - 30))

    # ---- scale & blit to fullscreen every frame ----
    scale = min(window_w / SCREEN_W, window_h / SCREEN_H)
    scaled_surface = pygame.transform.smoothscale(
        game_surface, (int(SCREEN_W * scale), int(SCREEN_H * scale))
    )
    x = (window_w - scaled_surface.get_width()) // 2
    y = (window_h - scaled_surface.get_height()) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (x, y))
    pygame.display.flip()

# ----------------------
# End of game: Game Over / Winner Screen
# ----------------------
game_surface.fill((20, 20, 40))  # dark background

if winner is None:
    winner = "Player" if player_score >= ai_score else "AI"

# Big result message
if winner.startswith("Player"):
    msg = "🎉 Congratulations! 🎉"
    color = (50, 255, 100)  # green
else:
    msg = "😢 Better Luck Next Time 😢"
    color = (255, 80, 80)   # red

msg_surface = big_font.render(msg, True, color)
msg_rect = msg_surface.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 50))
game_surface.blit(msg_surface, msg_rect)

# Winner line
txt = font.render(f"Winner: {winner}", True, (230, 230, 230))
txt_rect = txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 20))
game_surface.blit(txt, txt_rect)

# Score line
sub = font.render(f"Player Score: {player_score}   AI Score: {ai_score}", True, (200, 200, 200))
sub_rect = sub.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 60))
game_surface.blit(sub, sub_rect)

# --- scale and blit to fullscreen ---
scale = min(window_w / SCREEN_W, window_h / SCREEN_H) * 1.2  # a little larger if it fits
scaled_surface = pygame.transform.smoothscale(
    game_surface, (int(SCREEN_W * scale), int(SCREEN_H * scale))
)
x = (window_w - scaled_surface.get_width()) // 2
y = (window_h - scaled_surface.get_height()) // 2

screen.fill((0, 0, 0))
screen.blit(scaled_surface, (x, y))
pygame.display.flip()

pygame.time.wait(4000)
pygame.quit()
sys.exit()

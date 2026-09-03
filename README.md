# 🎮 Tetris vs AI

A competitive **Human vs AI Tetris game** built with Python and Pygame.

Instead of playing Tetris against yourself, this project turns the classic game into a head-to-head challenge: **you play on one board while an AI plays on another**. Both sides compete to clear lines, build the highest score, and survive as long as possible.

The AI doesn't simply make random moves—it evaluates possible placements using a board-state heuristic that considers **holes, aggregate height, bumpiness, and maximum column height** to select promising moves.

---

## ✨ Features

* 🤖 **AI-controlled Tetris opponent**
* 👤 **Human vs AI competitive gameplay**
* 🎯 Three difficulty levels:

  * Easy
  * Medium
  * Hard
* 🧠 AI move planning using board evaluation heuristics
* 🎲 Adjustable AI mistake probability based on difficulty
* ⚡ Dynamic difficulty adjustment during gameplay
* 🔥 Temporary **Power Jump** mechanic for the trailing player
* 👻 Ghost pieces showing where tetrominoes will land
* 🔮 Next-piece preview for the player
* 🧱 Line clearing and traditional Tetris mechanics
* 🏆 Automatic winner detection
* 🎉 Animated victory screen with confetti
* 🖥️ Fullscreen gameplay
* 🖱️ Mouse and keyboard menu controls
* 🔄 Ability to return to the main menu and play again

---

## 🧠 How the AI Works

The AI examines different possible positions and rotations for the current tetromino.

For every candidate move, it:

1. Tries a possible rotation.
2. Tries different horizontal positions.
3. Drops the piece to the lowest valid position.
4. Simulates placing the piece on the board.
5. Simulates line clearing.
6. Evaluates the resulting board.
7. Selects the move with the lowest heuristic score.

The board evaluation considers:

* **Holes** – empty spaces underneath placed blocks
* **Aggregate height** – total height of the columns
* **Bumpiness** – differences in height between neighboring columns
* **Maximum height** – height of the tallest column
* **Lines cleared** – rewarded separately

The current heuristic heavily penalizes holes while also discouraging unnecessarily high or uneven stacks.

### AI Imperfection

The AI intentionally isn't perfect.

Each difficulty level has a different probability of making a suboptimal move:

| Difficulty | AI Mistake Chance |
| ---------- | ----------------: |
| Easy       |               30% |
| Medium     |               12% |
| Hard       |                6% |

This makes the opponent feel more like a progressively challenging player rather than an unbeatable optimization algorithm.

---

## ⚔️ Dynamic Difficulty

The game also reacts to the current score difference.

If one side gains a significant lead, the game can increase that side's falling speed while giving the trailing side a temporary advantage.

The game uses score thresholds to dynamically modify falling speeds, helping prevent matches from becoming completely one-sided.

### ⚡ Power Jump

When the score difference becomes large enough, the trailing side receives a **Power Jump**.

The trailing player's score receives a temporary bonus, while the leading side is slowed down for a short period.

This creates a comeback mechanic and keeps the match competitive.

---

## 🎮 Controls

### In Game

| Key   | Action            |
| ----- | ----------------- |
| `←`   | Move piece left   |
| `→`   | Move piece right  |
| `↑`   | Rotate piece      |
| `↓`   | Soft drop         |
| `ESC` | Exit current game |

### Main Menu

| Key       | Action            |
| --------- | ----------------- |
| `← / →`   | Select difficulty |
| `SPACE`   | Start game        |
| `ESC / Q` | Exit              |

The menu also supports mouse interaction with **Start**, **Exit**, and **Main Menu** buttons.

---

## 🛠️ Technologies

* **Python**
* **Pygame**
* Object-oriented programming
* Game loop architecture
* Heuristic-based AI
* Collision detection
* Grid-based game logic
* Real-time event handling

---

## 📁 Project Structure

Currently, the project is implemented primarily in a single Python file:

```text
Tetris-vs-AI/
│
├── tetris1.py
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/tetris-vs-ai.git
cd tetris-vs-ai
```

### 2. Install the dependency

Make sure Python is installed, then install Pygame:

```bash
pip install pygame
```

### 3. Run the game

```bash
python tetris1.py
```

The game will launch in fullscreen mode and display the difficulty selection menu.

---

## 🎯 Gameplay

At the beginning of a match, choose between **Easy, Medium, or Hard**.

You and the AI then receive separate Tetris boards.

Both players:

* Receive tetrominoes
* Place pieces on their boards
* Clear completed lines
* Gain points
* Try to avoid topping out

Each cleared line awards **100 points**.

The first player to cause the opponent's board to fill or the opponent to top out wins.

If both boards become full simultaneously, the winner is determined by score.

---

## 🧩 Core Game Components

### Tetromino System

The game implements the seven standard Tetris tetromino shapes:

* I
* O
* T
* J
* L
* S
* Z

Pieces can be rotated and positioned on the board while collision detection prevents invalid placements.

### Ghost Piece

A ghost piece is rendered at the projected landing position, helping the player understand where the current tetromino will lock.

### Next Piece Preview

The player's upcoming tetromino is displayed beside the board, allowing the player to plan ahead.

---

## 🏗️ Technical Highlights

The project contains several interesting programming concepts:

### Grid-Based Game Representation

Each board is represented as a **20 × 10 grid**.

```text
20 rows × 10 columns
```

Each occupied cell stores a value representing the tetromino's color.

### Collision Detection

Before a piece moves or locks, the game checks whether its cells remain inside the board and whether they collide with existing blocks.

### AI Search

The AI searches across multiple rotations and horizontal positions before choosing its move.

### Wall Kicks

The game attempts small horizontal adjustments when a rotation would otherwise result in an invalid position, allowing pieces to rotate near walls and obstacles.

---

## 🔮 Possible Future Improvements

Some directions for expanding the project:

* [ ] Hold-piece mechanic
* [ ] Hard-drop functionality
* [ ] More advanced AI search
* [ ] Look-ahead AI using upcoming pieces
* [ ] Genetic algorithm / reinforcement-learning AI
* [ ] Online multiplayer
* [ ] Local multiplayer
* [ ] Sound effects and background music
* [ ] Persistent high-score system
* [ ] Match statistics
* [ ] AI decision visualization
* [ ] Replay system
* [ ] Modularize the project into multiple Python files
* [ ] Add automated tests
* [ ] Package the game as a standalone executable

---

## 📌 Project Goal

The goal of this project was to explore how **traditional game mechanics can be combined with AI decision-making**.

Rather than building a conventional Tetris clone, the project introduces an AI opponent and competitive balancing mechanics to create a more dynamic gameplay experience.

It serves as a practical exploration of:

> **Game development + heuristic AI + real-time decision making**

---

## 📜 License

This project is available for educational and personal use. Add a specific license (such as MIT) if you want to define formal reuse and distribution terms.

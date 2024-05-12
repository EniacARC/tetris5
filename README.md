# **Tetris 5**


This project is a multiplayer Tetris game implemented in Python using Pygame for the graphical user interface and network communication between clients and a server.
Gameplay Mechanics

# **Gameplay:**

Objective: The objective of the multiplayer Tetris game is to outlast your opponents by strategically placing falling Tetrominoes to create complete horizontal lines without leaving any gaps. As the game progresses, the speed of the falling Tetrominoes increases, challenging players to react quickly and make decisions under pressure.

**Controls:**

    Arrow Keys: Move Tetrominoes horizontally and rotate them clockwise.
    Down Arrow Key: Accelerate the fall of Tetrominoes.
    Up Arrow Key: Rotate Tetrominoes clockwise.

*Tetrominoes: The game features seven different Tetromino shapes, each consisting of four square blocks.*


    Falling Tetrominoes: Tetrominoes fall from the top to the bottom of the screen. Players can move and rotate the falling Tetrominoes to strategically place them on the game board.
    Clearing Lines: When a horizontal line is completely filled with blocks, it clears from the board, and any blocks above it move down. Clearing multiple lines simultaneously earns bonus points.
    Game Over: The game ends when the Tetromino stack reaches the top of the screen.

**Multiplayer Interaction:**

    Competitive Gameplay: Players compete against each other in real-time. The last player remaining without reaching the game over condition wins.
    Network Communication: The game communicates player moves and game state updates between clients and the server over a network connection, enabling seamless multiplayer gameplay.
    
**screenshot:**
![gameplay](https://github.com/EniacARC/tetris5/assets/94797541/8f6edfb3-a6bd-4918-9109-dd2bf184206c)


# *Installation and Usage*

*To play the game, follow these steps:*

    Clone the repository: git clone https://github.com/EniacARC/tetris5.git
    Install the required dependencies: pip install pygame
    Run the server script: python server.py
    Run 5 instances of the client script: python tetris.py

# Dependencies

    Python 3.x
    Pygame

# Credits

This project was created by Yonathan chapal.

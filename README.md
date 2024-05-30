# **Tetris 5**


This project is a multiplayer Tetris game implemented in Python using Pygame for the graphical user interface and network communication between clients and a server.

# **Gameplay:**

Objective: The objective of the multiplayer Tetris game is to outlast your opponents by strategically placing falling Tetrominoes to create complete horizontal lines without leaving any gaps. As the game progresses, the speed of the falling Tetrominoes increases, challenging players to react quickly and make decisions under pressure.

**Controls:**

    Arrow Keys: Move Tetrominoes horizontally.
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
![Screenshot_2](https://github.com/EniacARC/exc2-7-2/assets/94797541/9b2c125e-e897-4f88-82d7-ccbd0bf09c21)

---

# *sequence diagram + protocol:*
### sequence diagram:
![tetris_comms](https://github.com/EniacARC/tetris5/assets/94797541/c28583c4-72b3-426d-aa77-641804c2bf6c)

## explanation and protocol:

### tcp
client -> server: lines_to_add|game_over  
server -> client: msg_type (1 byte) + data (optional)  

### udp
client -> server: Board object (set size of 2400 bytes)  
server -> client: id (set size 64 bytes) + Board object (set size of 2400 bytes)  

### explanation
the server is connected to all the clients using tcp sockets and both the cliet and the server have listening udp sockets.  
the server hashes all the clients to generate them a unique id based on their addr and port.  
every time the board state changes the client send the updates board to the server and the server attaches the player's id and sends it to all the other players.  
every time a player clears a line a msg is sent to the server reflecting that. the server then sends to the another client a msg with type line to add x lines to his board.  
if a player was eliminated he will send a msg that he was eliminated. the server will then send a game_over type msg with the player id that was eliminated.  
if only 1 player remains the server sends a win_typ msg to the client.  


# *the main ideas in the planning of the project*
* disecting the game into classes so you can send each class over the network
* using both udp and tcp for immediate and general data
  - udp for the board class
  - tcp for game over updates and lines sent, both of which aren't time dependant
* try to minimise error by encapsulating and using try-catch 

---

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

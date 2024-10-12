# NeoChessBot
NeoChessBot is a upgraded version of [ChessBot](https://github.com/GNOLNG/ChessBot) that with more functions on Chess.com being accessible.
The original software addresses the lack of support for visually impaired users on Chess.com by introducing a keyboard-operated bot. The bot enables players to navigate the board and make moves using arrow keys and keyboard input, while also announcing the opponent's moves audibly.
The current version added more time control selection for Online Game. Game Reivew Function when game ended.

## Quick Start
1. Download the zip file that contain both source code and executable file.
2. Unzip and launch the software by simply clicking 'NeoChessBot.exe' 

## How to use
***Only two key to remember***
  - **1. Press Control + O, and the bot will tell options that you can make on that state.**
  - **2. Press Control + R to repeat the last sentence.**
---
***Start a chess game***
  - **1. press the "play with computer" button OR control + 1 to start a "vs computer" game**  
  - **2. press the "play with other online player" button OR control + 2 to start a "vs online players" game**
  - **3. Once the game is ready, the bot will tell the color you are playing**  

---

***Make a move***

  There are two modes supported to make a move: command mode and arrow mode

  - **For command mode: Control + F to focus on command panel.  Coordinate-based (UCI) style and Standard algebraic notation (SAN) style**  
    - **1. For SAN style:**

| SAN text            | Example meaning |
| ----------------- | ----------- |
| Nxe4 | knight capture on e4 |
| Rd1+ | rook move to d1 and check |
| qe7# | queen move to e7 and checkmate |
| o-o /0-0 | kingside castling (short castling) |
| o-o-o/ 0-0-0 | queenside castling (long castling) |
| e8=q | pawn move to e8 and promote to queen |

  - **2. For UCI style:**

| coordinate notation text            | Example meaning |
| ----------------- | ----------- |
| e2e4 | move piece on e2 to e4 |
| e7e8q | move piece on e7 (pawn) to e8 and promote to queen |

  - **3. After inputting a move, a confirm dialog shows up. Press enter or the space bar to confirm. Or press delete to cancel.** 

- **For arrow mode: Control + J to enter arrow mode**
  - **Use the arrow key to travel the chess board**
  - **Meanwhile, the bot will tell you the piece on that square.**
  - **Press space bar to select the target piece, travel to the square you wanted to place, and press the space bar again**
---

***Opponent Move***
  - **1. after your opponent makes their move, the bot will speak out their move**
  - For example, white pawn move to h8 and promote to queen and check
---
***Query information***
  - **1. Press "check remaining time" button to check the remaining time of the current game**
  - **2. Type piece name on "check position" input field to check the locations of that piece, e.g. knight / N**
  - **3. Type square name on "check position" input field to check the piece type on that square, e.g. a2**

---
***Game end***
  - **The game will end once either side wins or resigns from the chess game. The bot will tell you who wins and the reason, e.g. black wins by cheakmate**
  - **You must resign from the current game before starting another game**
  - **To resign, type the word "resign" and confirm it.**

---
***Game Review***
  - **Press 'A' (Analysis) to enter game review when game end. The bot will detect whether the game review limit is reached and announce to user.**
  - **After enter Game Review, the bot will provide the overall comment on your game.**
  - **In Game Review Mode, press 'Right Arrow Key' will go to the next move, 'Left Arrow Key' will go to the previous move. The feedback will be provided automatically for each move.
  - **Press 'E' (Explanation) to retrieve explanation of the current move. Sometimes the explanation will be 'None' as Chess.com does not provide any explanation.

## FAQ

#### Question: Why do I need to grant permission to use this software?

Answer: The chess bot will move the piece based on your input by controlling your mouse cursor, so please avoid moving your cursor after you confirm your move.

#### Question: Can I make pre-moves (move a piece before my opponent finishes their move)?

Answer: No, the current version of the application does not support pre-moves. You must wait for your opponent to complete their move before making your own.

#### Question: Do I need to log in to my Chess.com account every time I open the application?

Answer: No, you don't need to log in to your account again each time you open the application. Your account information will persist, and you will be automatically logged in when you open the application.

#### Question: How can I remove this software

Answer: You can delete the downloaded folder to remove the application completely.

#### Question: If I encountered error or I have any suggestions, is there any method to report it?

Answer: You can contact me through email tlkwok1214@gmail.com or tllkwok2-c@my.cityu.edu.hk

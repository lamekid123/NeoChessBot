# NeoChessBot
NeoChessBot is a upgraded version of [ChessBot](https://github.com/GNOLNG/ChessBot) with enhanced usability, functionality and reliability. New features such as Voice Input using Whisper Model, Operation and Guidance by Chat Bot, Puzzle Mode, New Board Detection Algorithm and a more informative interface. If you have tried the software, I would greatly appreciate any feedback through a brief satisfaction survey: https://forms.gle/5P7dv2KrFnR6aVSs5 

## Quick Start
1. Download the zip file of NeoChessBot and its related on https://github.com/lamekid123/NeoChessBot/releases/download/v1/NeoChessBot.zip
2. Unzip the file and double click 'NeoChessBot.exe' for launching.

## How to use
***Only few keys to remember***
  - **1. Press Tab Key to navigate different options on the keyboard base interface. It is the most straightforward way to use this software and it is similar to using a screen reader.**
  - **2. Press Control + O, and the bot will tell options that you can make on that state.**
  - **3. Press Control + R to repeat the last sentence.**
  - **4. Press W to summon a knowledgeable Chat Bot to handle your questions and requests.**
  - **5. Press Spacebar whenever you need to comfirm your choice.**
---
***Start a chess game***
  - **1. press the "play with computer" button OR control + 1 to start a "vs computer" game**  
  - **2. press the "play with other online player" button OR control + 2 to start a "vs online players" game**
  - **3. press the "Puzzle Mode" button OR control + 3 to start a rated puzzle game**
  - **4. Once the game is ready, the bot will tell the color you are playing. The pieces location will be provided in the beginning of a Chess Puzzle.**  

---

***Make a move***

  There are three ways supported to make a move: 1. Using the Keyboard-Base Interface in command mode. 2. Navigate through the chess board to select source and destination grids in Arrow Mode. 3. Speak out your move in UCI format when activated Voice Input function.

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
 
- **Voice Input: Press Control + S twice for a single input**
  - **The first Control + S indicates voice input activated and it will record your voice**
  - **The second Control + S terminate the recording session and process the audio to determine your voice input action**
  - **Most reliable format for moving chess piece: "Move {source grid} to {destination grid}" e.g. "Move E2 to E4"**
---

***Opponent Move***
  - **1. after your opponent makes their move, the bot will speak out their move**
  - For example, white pawn move to h8 and promote to queen and check
---
***Query information***
***When entered into a match, several information can be retrieved by navigating the Interface using Tab key and Arrow Key***
  - **1. Press "check remaining time" button to check the remaining time of the current game**
  - **2. Type piece name on "check position" input field to check the locations of that piece, e.g. knight / N**
  - **3. Type square name on "check position" input field to check the piece type on that square, e.g. a2**
  - **4. All the remaining pieces position will be displayed on "White Pieces" and "Black Pieces" field.**
  - **5. The moves of the game will displayed on the "Move List" field.**
  - **6. Press the "Macro View" Button to realize which vulnerable pieces are being attacked.**
  - **7. All these information can be obtained using tab key, arrow key and spacebar**

---
***Game end***
  - **The game will end once either side wins or resigns from the chess game. The bot will tell you who wins and the reason, e.g. black wins by cheakmate**
  - **You must resign from the current game before starting another game**
  - **To resign, type the word "resign" and confirm it.**

---
***Game Review***
  - **Press 'A' (Analysis) or "Game Review" Button to enter game review when the game is finished. The bot will detect whether the game review limit is reached and announce to user.**
  - **After enter Game Review, the bot will provide the overall comment on your game.**
  - **In Game Review Mode, press 'Right Arrow Key' will go to the next move, 'Left Arrow Key' will go to the previous move. The feedback will be provided automatically for each move.**
  - **Explanation field provides the explanation of the current move given by the Chess Engine. Sometimes the explanation will be 'None' as Chess.com does not provide any explanation.**
  - **Press 'B' or "Best Move" Button to get the Best Move of the Board provided by the Chess Engine.**

---
***Puzzle Mode***
  - **Press Ctrl 3 Button or Puzzle Mode button to enter a rated puzzle game.**
  - **Your assigned color and the Chess Pieces will be provided at the beginning for each new puzzle.**
  - **Instead of listen to the dull announcement, you can navigate the board using arrow mode to feel the position of each pieces.**
  - **The rated puzzle game has unlimited time which you can think deeply about the puzzle, but there are limited puzzle for free account each day.**
  - **When solved the puzzle, you can choose to start a new puzzle, retry the puzzle or return to home page for other game mode.**

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

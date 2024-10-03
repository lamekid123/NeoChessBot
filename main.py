import sys
import os
from functools import partial
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QDialogButtonBox,
    QDialog,
    QMainWindow,
    QApplication,
    QHBoxLayout,
    QMessageBox,
    QCheckBox,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QTimer, QRect, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QIcon


from Components.board_detection_component import detectChessboard, userColor        ## header file
from Components.piece_move_component import widgetDragDrop, widgetClick, moveLeft, moveRight, moveUp, moveDown, moveTopLeft, moveBottomLeft, moveBottomRight, moveTopRight 
from Components.chess_validation_component import ChessBoard
from Components.speak_component import TTSThread
from Components.stockfish_component import stockfish_adviser
from Utils.enum_helper import (
    Input_mode,
    Bot_flow_status,
    Game_flow_status,
    Speak_template,
    Game_play_mode,
    determinant,
    bot_List,
    timeControl,
    timeControlDeterminant,
    keyPressed
)
from PyQt6 import QtWidgets

import pyaudio
import wave
import whisper
import torch

import js_function

import time

PIECE_TYPE_CONVERSION = {
    "q": "queen",
    "n": "knight",
    "r": "rook",
    "b": "bishop",
    "p": "pawn",
    "k": "king",
    "none": "empty",
}

CHESSBOARD_LOCATION_CONVERSION = {
    "a": "1",
    "b": "2",
    "c": "3",
    "d": "4",
    "e": "5",
    "f": "6",
    "g": "7",
    "h": "8",
}

PIECES_SHORTFORM_CONVERTER = {
    "Q": "white queen",
    "N": "white knight",
    "R": "white rook",
    "B": "white bishop",
    "P": "white pawn",
    "K": "white king",

    "q": "black queen",
    "n": "black knight",
    "r": "black rook",
    "b": "black bishop",
    "p": "black pawn",
    "k": "black king",
}


class LeftWidget(QWidget):
    """
    This class respresent the left widget.\n
    It contains chess.com web view and invisible grids that assigned after board detection
    """

    key_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.chessWebView = QWebEngineView()

        # profile to store the user account detail
        self.profile = QWebEngineProfile("storage", self.chessWebView)
        self.profile.setPersistentStoragePath(
            os.path.join(current_dir, "Tmp", "chess_com_account")
        )

        web_page = QWebEnginePage(self.profile, self.chessWebView)
        self.chessWebView.setPage(web_page)
        self.chessWebView.load(QUrl("https://www.chess.com"))

        self.chessWebView.setMinimumSize(1000, 550)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.chessWebView)
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlayout)

        self.userLoginName = ""
        self.grids = dict()

    # check whether user logined
    def checkLogined(self):
        def callback(x):
            self.userLoginName = x

        jsCode = """
            function checkLogin() {{
                return document.querySelector(".home-user-info")?.outerText
            }}
            checkLogin();
            """
        self.chessWebView.page().runJavaScript(jsCode, callback)

    # crawl remaining time
    def checkTime(self, callBack):
        jsCode = """
            function checkTime() {{
                clocks = document.querySelectorAll(".clock-time-monospace")
                return [clocks[0].outerText, clocks[1].outerText]
            }}
            checkTime();
            """

        return self.chessWebView.page().runJavaScript(jsCode, callBack)
    
    def keyPressEvent(self, event):
        self.key_signal.emit(event.key())

class CheckBox(QCheckBox):
    """
    CheckBox class that allowd check by enter
    """

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.nextCheckState()
        super(CheckBox, self).keyPressEvent(event)


class RightWidget(QWidget):
    """
    This class respresent the right widget.\n
    It contains command panel , query place.
    """

    def checkBoxStateChanged(self, state):
        global internal_speak_engine
        print(state)
        if state == 2:
            internal_speak_engine = True
        else:
            internal_speak_engine = False

    def __init__(self):
        super().__init__()
        global internal_speak_engine

        self.screen_reader_checkBox = QCheckBox("Use internal speak engine")
        self.screen_reader_checkBox.setChecked(True)
        self.screen_reader_checkBox.stateChanged.connect(self.checkBoxStateChanged)
        self.screen_reader_checkBox.setAccessibleName("Use internal speak engine")
        self.screen_reader_checkBox.setAccessibleDescription(
            "tick to use internal speak engine"
        )

        self.playWithComputerButton = QPushButton("Play with computer")
        self.playWithComputerButton.setText("Play with computer")
        self.playWithComputerButton.setAccessibleName("Play with computer")
        self.playWithComputerButton.setAccessibleDescription(
            "press enter to play with computer engine"
        )

        self.playWithComputerButton_BackToSchoolButton = QPushButton("Back To School")
        self.playWithComputerButton_Coach = QPushButton("Coach")
        self.playWithComputerButton_Adaptive = QPushButton("Adaptive")
        self.playWithComputerButton_Beginner = QPushButton("Beginner")
        self.playWithComputerButton_Intermediate = QPushButton("Intermediate")
        self.playWithComputerButton_Advanced = QPushButton("Advanced")
        self.playWithComputerButton_Master = QPushButton("Master")
        self.playWithComputerButton_Athletes = QPushButton("Athletes")
        self.playWithComputerButton_Musicians = QPushButton("Musicians")
        self.playWithComputerButton_Creators = QPushButton("Creators")
        self.playWithComputerButton_TopPlayers = QPushButton("Top Players")
        self.playWithComputerButton_Personalities = QPushButton("Personalities")
        self.playWithComputerButton_Engine = QPushButton("Engine")

        self.playWithOtherButton = QPushButton("Play with other online player")
        self.playWithOtherButton.setAccessibleName("Play with other online player")
        self.playWithOtherButton.setAccessibleDescription(
            "press enter to play with other online player"
        )

        # self.playWithOther_Bullet_Button = QPushButton("Bullet")
        # self.playWithOther_Blitz_Button = QPushButton("Blitz")
        # self.playWithOther_Rapid_Button = QPushButton("Rapid")

        self.playWithOther_Bullet_1_0_Button = QPushButton("1 + 0")
        self.playWithOther_Bullet_1_1_Button = QPushButton("1 + 1")
        self.playWithOther_Bullet_2_1_Button = QPushButton("2 + 1")

        self.playWithOther_Blitz_3_0_Button = QPushButton("3 + 0")
        self.playWithOther_Blitz_3_2_Button = QPushButton("3 + 2")
        self.playWithOther_Blitz_5_0_Button = QPushButton("5 + 0")

        self.playWithOther_Rapid_10_0_Button = QPushButton("10 + 0")
        self.playWithOther_Rapid_15_10_Button = QPushButton("15 + 10")
        self.playWithOther_Rapid_30_0_Button = QPushButton("30 + 0")

        self.playWithOther_Bullet_1_0_Button.setAutoDefault(True)
        self.playWithOther_Bullet_1_1_Button.setAutoDefault(True)
        self.playWithOther_Bullet_2_1_Button.setAutoDefault(True)
        self.playWithOther_Blitz_3_0_Button.setAutoDefault(True)
        self.playWithOther_Blitz_3_2_Button.setAutoDefault(True)
        self.playWithOther_Blitz_5_0_Button.setAutoDefault(True)
        self.playWithOther_Rapid_10_0_Button.setAutoDefault(True)
        self.playWithOther_Rapid_15_10_Button.setAutoDefault(True)
        self.playWithOther_Rapid_30_0_Button.setAutoDefault(True)

        self.puzzleModeButton = QPushButton("Puzzle Mode")

        self.playWithComputerButton.setAutoDefault(True)
        self.playWithOtherButton.setAutoDefault(True)
        self.puzzleModeButton.setAutoDefault(True)

        self.colorBox = QLabel()
        self.colorBox.setText("Assigned Color: ")

        self.opponentBox = QLabel()
        self.opponentBox.setText("Opponent last move: \n")

        self.check_time = QPushButton("Check remaining time")
        self.check_time.setAutoDefault(True)

        self.resign = QPushButton("Resign")
        self.resign.setAutoDefault(True)

        self.check_position = QLineEdit()
        self.check_position.setPlaceholderText("Check position")
        self.check_position.setAccessibleName("Check position input field")
        self.check_position.setAccessibleDescription(
            "you can query a piece or square here"
        )

        self.commandPanel = QLineEdit()
        self.commandPanel.setPlaceholderText("Move Input")
        self.commandPanel.setAccessibleName("Command Panel")
        self.commandPanel.setAccessibleDescription("You can type your move here")
        
        self.selectPanel = QLineEdit()
        self.selectPanel.setPlaceholderText("Enter Selection")

        font = QFont()
        font.setPointSize(18)
        self.commandPanel.setFont(font)
        self.check_position.setFont(font)

        self.setting_menu = []
        self.setting_menu.append(self.playWithComputerButton)
        self.setting_menu.append(self.playWithOtherButton)
        self.setting_menu.append(self.puzzleModeButton)

        self.play_menu = []
        self.play_menu.append(self.colorBox)
        self.play_menu.append(self.opponentBox)
        self.play_menu.append(self.resign)
        self.play_menu.append(self.check_time)
        self.play_menu.append(self.check_position)
        self.play_menu.append(self.commandPanel)

        self.online_mode_select_menu = []
        self.online_mode_select_menu.append(self.playWithOther_Bullet_1_0_Button)
        self.online_mode_select_menu.append(self.playWithOther_Bullet_1_1_Button)
        self.online_mode_select_menu.append(self.playWithOther_Bullet_2_1_Button)
        self.online_mode_select_menu.append(self.playWithOther_Blitz_3_0_Button)
        self.online_mode_select_menu.append(self.playWithOther_Blitz_3_2_Button)
        self.online_mode_select_menu.append(self.playWithOther_Blitz_5_0_Button)
        self.online_mode_select_menu.append(self.playWithOther_Rapid_10_0_Button)
        self.online_mode_select_menu.append(self.playWithOther_Rapid_15_10_Button)
        self.online_mode_select_menu.append(self.playWithOther_Rapid_30_0_Button)

        self.setting_layout = QVBoxLayout()
        # self.setting_layout.addWidget(self.screen_reader_checkBox)
        for item in self.setting_menu:
            self.setting_layout.addWidget(item)

        for item in self.play_menu:
            self.setting_layout.addWidget(item)
            item.hide()

        for item in self.online_mode_select_menu:
            self.setting_layout.addWidget(item)
            item.hide()
        self.setLayout(self.setting_layout)


##confirm popup dialog that show and speak the message
class confirmDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)

        self.setWindowTitle("confirm dialog")
        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        def dialog_helper_menu():
            speak("press enter to confirm. <> or press delete to cancel")

        self.layout = QVBoxLayout()
        message = "confirm " + message
        self.layout.addWidget(QLabel(message))
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        shortcut_O = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_O.activated.connect(dialog_helper_menu)
        shortcut_R = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_R.activated.connect(partial(speak, message))
        speak(message)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
            print("cancel clicked")
            speak("Cancel")
            self.reject()


class MainWindow(QMainWindow):
    """
    Merge left and right widget, and act as middle man for communication\n
    Control the application status, implement functionality to left and right widget.\n
    Handle all logic operation
    """

    def show_information_box(self):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Information")
        message_box.setText("This is an information message.")
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.setFocus()
        message_box.exec()

    ##change the application flow status and re-init / clean the variable
    def change_main_flow_status(self, status):
        print("change status", status)
        match status:
            case Bot_flow_status.setting_status:
                self.getOpponentMoveTimer.stop()
                self.check_game_end_timer.stop()
                self.getScoreTimer.stop()
                self.main_flow_status = Bot_flow_status.setting_status
                self.game_flow_status = Game_flow_status.not_start
                self.input_mode = Input_mode.command_mode
                self.rightWidget.commandPanel.setAccessibleDescription(
                    "type the letter 'C' for computer mode, type the letter 'O' for online players mode "
                )
                self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H"]
                self.number = ["1", "2", "3", "4", "5", "6", "7", "8"]
                self.chessBoard = None
                self.rightWidget.colorBox.setText("Assigned Color: ")
                self.userColor = None
                self.opponentColor = None
                self.rightWidget.right_layout = self.rightWidget.setting_layout
                self.rightWidget.opponentBox.setText("Opponent move: \n")
                for label in self.leftWidget.grids.values():
                    label.deleteLater()
                for item in self.rightWidget.play_menu:
                    item.hide()
                for item in self.rightWidget.setting_menu:
                    item.show()
                self.rightWidget.playWithComputerButton.setFocus()
                self.currentFoucs = 0
                self.leftWidget.grids = dict()
                return
                
            case Bot_flow_status.select_status:
                self.main_flow_status = Bot_flow_status.select_status
                self.currentFoucs = 0
                for item in self.rightWidget.setting_menu:
                    item.hide()
                match self.game_play_mode:
                    case Game_play_mode.computer_mode:
                        self.default_bot()
                    case Game_play_mode.online_mode:
                        for item in self.rightWidget.online_mode_select_menu:
                            item.show()
                        self.rightWidget.playWithOther_Bullet_1_0_Button.setFocus()
                        speak("Select Time Controls")
                return

            case Bot_flow_status.board_init_status:
                self.main_flow_status = Bot_flow_status.board_init_status

                self.leftWidget.chessWebView.loadFinished.connect(
                    partial(print, "connect")
                )
                self.leftWidget.chessWebView.loadFinished.disconnect()
                self.getOpponentMoveTimer.stop()
                self.check_game_end_timer.stop()
                self.getScoreTimer.stop()
                self.input_mode = Input_mode.command_mode
                for item in self.rightWidget.setting_menu:
                    item.hide()
                for item in self.rightWidget.play_menu:
                    item.show()
                self.chessBoard = None
                self.userColor = None
                self.moveList = []
                self.opponentColor = None
                self.leftWidget.grids = dict()
                return
            
            case Bot_flow_status.game_play_status:
                self.check_game_end_timer.start(2000)
                self.rightWidget.commandPanel.setFocus()
                self.currentFoucs = len(self.rightWidget.play_menu)
                with open ("./stockfishTicket.txt", 'w') as stockfishTicket:
                    stockfishTicket.write('3')
                self.main_flow_status = Bot_flow_status.game_play_status
                return

    ##initialize a vs computer game for user
    def playWithComputerHandler(self):
        if self.main_flow_status == Bot_flow_status.board_init_status:
            speak("Still " + Speak_template.initialize_game_sentense.value, True)
            return
        if (
            self.main_flow_status == Bot_flow_status.game_play_status
            and not self.game_flow_status == Game_flow_status.game_end
        ):
            speak("Please resign before start a new game", True)
            return
        print("computer mode selected")
        self.change_main_flow_status(Bot_flow_status.board_init_status)
        self.game_play_mode = Game_play_mode.computer_mode
        speak(
            "computer engine mode <>" + Speak_template.initialize_game_sentense.value,
            True,
        )
        self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(2000, self.checkExistGame))

        self.leftWidget.chessWebView.load(
            QUrl("https://www.chess.com/play/computer/komodo1")
        )

    def default_bot(self):
        def clickNCapture():
            if not self.main_flow_status == Bot_flow_status.game_play_status:
                self.initBoard()
                self.getColor()
                self.getBoard()
        
        if self.leftWidget.userLoginName != None:
            self.clickWebButton(
                [("button", "start"), ("button", "choose"), ("button", "play")],
                0,
                clickNCapture,
                0,
            )
        else:
            self.clickWebButton(
                [("button", "start"), ("button", "choose"), ("button", "play")],
                0,
                clickNCapture,
                0,
            )

    ##initialize a vs online player game for user
    def playWithOtherButtonHandler(self):  ###url
        if self.main_flow_status == Bot_flow_status.board_init_status:
            speak("Still " + Speak_template.initialize_game_sentense.value, True)
            return
        if (
            self.main_flow_status == Bot_flow_status.game_play_status
            and not self.game_flow_status == Game_flow_status.game_end
        ):
            speak("Please resign before start a new game", True)
            return
        print("online mode selected")
        speak(
            "online player mode <>" + Speak_template.initialize_game_sentense.value,
            True,
        )
        self.game_play_mode = Game_play_mode.online_mode
        self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(1500, self.checkExistGame))
        self.leftWidget.chessWebView.load(QUrl("https://www.chess.com/play/online"))

    def selectPanelHandler(self):
        input = self.rightWidget.selectPanel.text().lower()
        if(self.game_play_mode == Game_play_mode.computer_mode):
            print("no idea")
        elif(self.game_play_mode == Game_play_mode.online_mode):
            for selection in timeControlDeterminant:
                if input in selection.value:
                    self.online_select_timeControl(selection.value[input])
        
    def online_select_timeControl(self, timeControl):
        def clickNCapture(x):
            def test(clocks):
                if clocks == None or clocks[0] == clocks[1]:
                        self.leftWidget.checkTime(test)
                else:
                    print("clocks detected :", clocks)
                    self.initBoard()
                    self.getColor()
                    self.getBoard()
            self.leftWidget.checkTime(test)
        
        print(f"timeControl = {timeControl}")
        for item in self.rightWidget.online_mode_select_menu:
            item.hide()
        for item in self.rightWidget.play_menu:
            item.show()
        if self.leftWidget.userLoginName != None:
            print("login name", self.leftWidget.userLoginName)
            self.leftWidget.chessWebView.page().runJavaScript(js_function.clickTimeControlButton + f"clickTimeControlButton('{timeControl}', true)", clickNCapture)
        else:
            print("No login")
            self.leftWidget.chessWebView.page().runJavaScript(js_function.clickTimeControlButton + f"clickTimeControlButton('{timeControl}', false)", clickNCapture)

    def checkExistGame(self):
        def callback(moveList):
            print(f"movemovmeomvomeovmo = {moveList}")
            if(moveList):
                def getResult(x):
                    self.FenNotation = x
                    self.getBoard(self.FenNotation)
                    self.change_main_flow_status(Bot_flow_status.game_play_status)
                    print(f"self.FenNotation = {self.FenNotation}")

                self.change_main_flow_status(Bot_flow_status.board_init_status)
                self.initBoard()
                self.getColor()
                self.leftWidget.chessWebView.page().runJavaScript(js_function.clickShare)
                QTimer.singleShot(500, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.getFEN, getResult))
                print("reconstructing the board")

                for move in moveList:
                    self.moveList.append(move)
           
                print(f"movelist = {self.moveList}")
                self.previous_game_exist = True
                turn = "WHITE" if(len(self.moveList)%2==0) else "BLACK"
                self.game_flow_status = Game_flow_status.user_turn if(turn==self.userColor) else Game_flow_status.opponent_turn
                print("Existing Game Founded")                      
                return

            else:
                print("no existing board")
                self.change_main_flow_status(Bot_flow_status.select_status)

        self.leftWidget.chessWebView.loadFinished.disconnect()
        self.leftWidget.chessWebView.page().runJavaScript(js_function.checkExistGame, callback)

    def puzzleModeHandler(self):
        self.game_play_mode = Game_play_mode.puzzle_mode
        self.main_flow_status = self.change_main_flow_status(Bot_flow_status.board_init_status)
        self.leftWidget.chessWebView.load(QUrl("https://www.chess.com/puzzles/rated"))
        self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(2000, self.puzzle_mode_InitBoard))

    def puzzle_mode_InitBoard(self):
        self.puzzle_mode_GetTitle()
        self.puzzle_mode_ConstructBoard()

    def puzzle_mode_ConstructBoard(self):
        def callback(board):
            self.FenNotation = ""
            self.boardDescription = []
            for row in reversed(range(8)):
                count = 0
                for column in range(8):
                    if(board[row][column]!=0):
                        alphabet_column = list(CHESSBOARD_LOCATION_CONVERSION.keys())[list(CHESSBOARD_LOCATION_CONVERSION.values()).index(str(column+1))]
                        piece_loc = PIECES_SHORTFORM_CONVERTER[board[row][column]] + " on " + alphabet_column + str(row+1)
                        self.boardDescription.append(piece_loc)
                        if(count!=0):
                            self.FenNotation += str(count) + board[row][column]
                            count = 0
                        else:
                            self.FenNotation += board[row][column]
                    else:
                        count += 1
                        if(column==7):
                            self.FenNotation += str(count)
                    print(board[row][column], end=" ")
                if(row!=0):
                    self.FenNotation += "/"
                print()
            if(self.userColor=="WHITE"):
                self.FenNotation += " w "
                if(board[0][4]=="K"):
                    if(board[0][0]=="R"):
                        self.FenNotation += "K"
                    if(board[0][7]=="R"):
                        self.FenNotation += "Q"
                self.FenNotation += "kq"
            else:
                self.FenNotation += " b KQ"
                if(board[7][4]=="k"):
                    if(board[7][7]=="r"):
                        self.FenNotation += "k"
                    if(board[7][0]=="r"):
                        self.FenNotation += "q"
            print(self.FenNotation)
            print(self.boardDescription)
            self.chessBoard = ChessBoard(self.FenNotation)
            self.change_main_flow_status(Bot_flow_status.game_play_status)
            self.game_flow_status = Game_flow_status.opponent_turn
            self.puzzle_mode_GetTitle()

        self.leftWidget.chessWebView.page().runJavaScript(js_function.puzzle_mode_constructBoard, callback)


    def puzzle_mode_GetTitle(self):
        def callback(title):
            if(self.userColor == None):
                match title:
                    case "White":
                        self.userColor = title.upper()
                        self.opponentColor = "BLACK"
                        print(f"User: {self.userColor}, Oppoenent: {self.opponentColor}")
                    case "Black":
                        self.userColor = title.upper()
                        self.opponentColor = "WHITE"
                        print(f"User: {self.userColor}, Oppoenent: {self.opponentColor}")
            else:
                match title:
                    case "Correct":
                        print("Correct")
                        self.userColor = None
                        self.game_flow_status = self.change_main_flow_status(Bot_flow_status.board_init_status)
                        self.clickNextPuzzle()
                    #button click next
                    case "Incorrect":
                        print("Incorrect, puzzle run ended")
                        self.change_main_flow_status(Bot_flow_status.setting_status)
                    case _:
                        # self.puzzle_getOppMove_sgn.emit()
                        self.puzzle_mode_GetMove()

        self.leftWidget.chessWebView.page().runJavaScript(js_function.puzzle_mode_GetTitle, callback)

    def puzzle_mode_GetMove(self):
        def callback(uci_move):
            print(uci_move)
            pos1 = uci_move[0] + uci_move[1]
            pos2 = uci_move[2] + uci_move[3]
            pos1_piece = self.chessBoard.check_grid(pos1)
            if(pos1_piece==None):
                dest = pos1
                src = pos2
                uci_move = src + dest
            else:
                dest = pos2
                src = pos1
                
            if(self.game_flow_status == Game_flow_status.opponent_turn):
                print(f"Opponent Move {src} to {dest}")
                speak(f"Opponent Move {src} to {dest}")
                self.chessBoard.moveWithValidate(uci_move)
                self.game_flow_status = Game_flow_status.user_turn
            else:
                print("no update move")
                return

        self.leftWidget.chessWebView.page().runJavaScript(js_function.puzzle_mode_GetOpponentMove, callback)

    def puzzle_movePiece(self, move):
        def checkSuccess(success):
            if(success):
                print("Move successfully")
                self.game_flow_status = Game_flow_status.opponent_turn
            else:
                self.chessBoard.board_object.pop()
                print("Move not success, please do not move your mouse while moving pieces.")

        def callback(pos):
            print(pos)
            x = pos[0]
            y = pos[1]
            interval = pos[2]
            if self.userColor=="WHITE":
                if(dest[0]>src[0] and dest[1]==src[1]):    
                    moveRight(x, y, x_scale, interval)
                elif(dest[0]<src[0] and dest[1]==src[1]):
                    moveLeft(x, y, x_scale, interval)
                elif(dest[0]==src[0] and dest[1]>src[1]):
                    moveUp(x, y, y_scale, interval)
                elif(dest[0]==src[0] and dest[1]<src[1]):
                    moveDown(x, y, y_scale, interval)
                elif(dest[0]>src[0] and dest[1]>src[1]):
                    moveTopRight(x, y, x_scale, y_scale, interval)
                elif(dest[0]>src[0] and dest[1]<src[1]):
                    moveBottomRight(x, y, x_scale, y_scale, interval)
                elif(dest[0]<src[0] and dest[1]>src[1]):
                    moveTopLeft(x, y, x_scale, y_scale, interval)
                elif(dest[0]<src[0] and dest[1]<src[1]):
                    moveBottomLeft(x, y, x_scale, y_scale, interval)
            else:
                if(dest[0]<src[0] and dest[1]==src[1]):    
                    moveRight(x, y, x_scale, interval)
                elif(dest[0]>src[0] and dest[1]==src[1]):
                    moveLeft(x, y, x_scale, interval)
                elif(dest[0]==src[0] and dest[1]<src[1]):
                    moveUp(x, y, y_scale, interval)
                elif(dest[0]==src[0] and dest[1]>src[1]):
                    moveDown(x, y, y_scale, interval)
                elif(dest[0]<src[0] and dest[1]<src[1]):
                    moveTopRight(x, y, x_scale, y_scale, interval)
                elif(dest[0]<src[0] and dest[1]>src[1]):
                    moveBottomRight(x, y, x_scale, y_scale, interval)
                elif(dest[0]>src[0] and dest[1]<src[1]):
                    moveTopLeft(x, y, x_scale, y_scale, interval)
                elif(dest[0]>src[0] and dest[1]>src[1]):
                    moveBottomLeft(x, y, x_scale, y_scale, interval)

            QTimer.singleShot(10, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.checkMoveSuccess + f"checkMoveSuccess({loc})", checkSuccess))
            QTimer.singleShot(1000, self.focus_back)
                

        movePair = self.chessBoard.moveWithValidate(move)
        if(movePair == "Illegal move" or movePair == "Invalid move"):
            print(movePair)
            return
        uci_string = ""
        screen = self.screen().geometry()
        left = screen.left()
        top = screen.top()
        if(len(movePair)==2):
            uci_string = movePair[0]
        if(len(uci_string)==4):
            src = uci_string[:2].lower()
            dest = uci_string[2:4].lower()
        loc = CHESSBOARD_LOCATION_CONVERSION[src[0]] + src[1]
        x_scale = abs(ord(dest[0])-ord(src[0]))
        y_scale = abs(int(dest[1])-int(src[1]))
        self.leftWidget.chessWebView.page().runJavaScript(js_function.getCoordinate + f"getCoordinate({loc}, {left}, {top})", callback)
        

    def clickNextPuzzle(self):
        def callback(x):
            QTimer.singleShot(2000, self.puzzle_mode_InitBoard)

        self.leftWidget.chessWebView.page().runJavaScript(js_function.clickNextPuzzle, callback)

    ##convert move to human readable form
    def move_to_human_form(self, attackerColor, uciString, sanString):
        counter_color = "WHITE" if attackerColor == "BLACK" else "BLACK"
        human_string = attackerColor
        uciString = str(uciString).lower()
        sanString = str(sanString).lower()
        target_square = uciString[:2]
        dest_square = uciString[2:4]

        self.chessBoard.board_object.pop()

        en_passant = self.chessBoard.board_object.has_legal_en_passant()
        target_piece_type = self.chessBoard.check_grid(target_square).__str__().lower()

        dest_piece_type = self.chessBoard.check_grid(dest_square).__str__().lower()

        print(target_piece_type, dest_piece_type)
        # self.chessBoard.moveWithValidate(sanString)
        if sanString.count("x"):
            human_string = (
                human_string
                + " "
                + PIECE_TYPE_CONVERSION[target_piece_type]
                + " captures"
            )
            if en_passant and target_piece_type == "p" and dest_piece_type == None:
                human_string = (
                    human_string + " on " + dest_square.upper() + " en passant"
                )
            else:
                human_string = (
                    human_string
                    + " "
                    + counter_color
                    + " "
                    + PIECE_TYPE_CONVERSION[dest_piece_type]
                    + " on "
                    + dest_square.upper()
                )
        else:
            human_string = (
                human_string
                + " "
                + PIECE_TYPE_CONVERSION[target_piece_type]
                + " moves to "
                + dest_square
            )

        if sanString.count("O-O-O"):
            human_string = human_string + " queenside castling"
        elif sanString.count("O-O"):
            human_string = human_string + " kingside castling"
        elif sanString.count("="):
            human_string = (
                human_string
                + " and promoted to "
                + PIECE_TYPE_CONVERSION[
                    sanString[sanString.index("=") + 1].__str__().lower()
                ]
            )

        if sanString.count("+"):
            human_string = human_string + " and check "
        self.chessBoard.moveWithValidate(sanString)
        print(human_string)
        return human_string

    ##check the score when end game
    def check_score(self):
        def callBack(x):
            if (
                not self.game_flow_status == Game_flow_status.game_end
                or not self.game_play_mode == Game_play_mode.online_mode
            ):
                self.getScoreTimer.stop()
                return
            if not x == None and (x[0] or x[1]):
                speak_string = ""
                print("rating: ", x[0], "league: ", x[1])
                if not x[0] == None:
                    speak_string = speak_string + "rating " + x[0]
                if not x[1] == None:
                    speak_string = speak_string + "league " + x[1]
                self.getScoreTimer.stop()
                speak(speak_string)
            else:
                self.getScoreTimer.start(1000)

        jsCode = """
            function checkScore(){{
                rating = document.querySelectorAll(".rating-score-component")[1]
                league = document.querySelectorAll(".league-score-component")[0]

                if(!rating.textContent){{
                    rating = null 
                }}
                else{{
                    rating = rating.textContent?.trim()
                }}

                if(!league.textContent){{
                    league = null 
                }}
                else{{
                    league = rating.textContent?.trim()
                }}
                return [rating, league]
            }}

            checkScore();
        """
        return self.leftWidget.chessWebView.page().runJavaScript(jsCode, callBack)

    ##click resign button on web view
    def resign_handler(self):
        dlg = confirmDialog("to resign from current game.")
        if dlg.exec():
            self.change_main_flow_status(Bot_flow_status.setting_status)

            def callBack():
                self.game_flow_status = Game_flow_status.game_end
                speak(Speak_template.user_resign.value)
                self.getOpponentMoveTimer.stop()
                self.getScoreTimer.start(1000)
                return

            if (
                self.leftWidget.userLoginName == None
                or self.game_play_mode == Game_play_mode.computer_mode
            ):
                self.clickWebButton(
                    [
                        ("button", "abort"),
                        ("button", "resign"),
                        ("button", "yes", True),
                    ],
                    0,
                    callBack,
                    0,
                )
            else:
                self.clickWebButton(
                    [
                        ("button", "abort"),
                        ("button", "resign"),
                        ("button", "yes", True),
                    ],
                    0,
                    callBack,
                    0,
                )
        else:
            speak("Cancel!")

    ##handle check position query, user input square name or piece type to check the location
    def check_position_handler(self):
        input = self.rightWidget.check_position.text().lower()
        print(any(char.isdigit() for char in input))
        if any(char.isdigit() for char in input):
            grid = input
            piece = self.chessBoard.check_grid(grid).__str__()
            speak_sentence = grid.upper()

            print(piece)
            if not piece == "Invalid square name":
                if not piece == "None":
                    if piece.__str__().islower():
                        speak_sentence = speak_sentence + " BLACK "
                    else:
                        speak_sentence = speak_sentence + " WHITE "
                    speak(
                        speak_sentence + PIECE_TYPE_CONVERSION[piece.__str__().lower()]
                    )
                else:
                    speak(speak_sentence + " empty")
            else:
                speak(speak_sentence)
            self.rightWidget.check_position.clear()
            return
        else:
            piece_type = input
            try:
                piece_type = PIECE_TYPE_CONVERSION[piece_type]
            except Exception as e:
                print(e)
            grid = self.chessBoard.check_piece(piece_type)
            speak_string = ""
            white = grid["WHITE"]
            if len(white) > 0:
                speak_string = (
                    speak_string
                    + len(white).__str__()
                    + " WHITE "
                    + piece_type
                    + white.__str__().upper()
                )
            else:
                speak_string = speak_string + "NO WHITE " + piece_type + "found "

            speak_string = speak_string + " and "
            black = grid["BLACK"]
            if len(white) > 0:
                speak_string = (
                    speak_string
                    + len(black).__str__()
                    + " BLACK "
                    + piece_type
                    + black.__str__().upper()
                )
            else:
                speak_string = speak_string + "NO BLACK " + piece_type + "found "
            speak(speak_string)
            self.rightWidget.check_position.clear()
            return

    def focus_back(self):
            if self.input_mode == Input_mode.arrow_mode:
                self.leftWidget.grids[self.currentFoucs].setFocus()
            else:
                self.rightWidget.commandPanel.setFocus()
            return
    
    ## interpret the input command and perform different task accordingly
    def CommandPanelHandler(self):

        input = self.rightWidget.commandPanel.text().lower()

        if input.count("computer") or input == "c":
            self.playWithComputerHandler()
            self.rightWidget.commandPanel.clear()
            return
        elif input.count("online") or input == "o":
            self.playWithOtherButtonHandler()
            self.rightWidget.commandPanel.clear()
            return
        if self.game_play_mode == Game_play_mode.puzzle_mode:
            if self.game_flow_status == Game_flow_status.user_turn:
                self.puzzle_movePiece(input)
                QTimer.singleShot(2000, self.puzzle_mode_GetTitle)
            else:
                speak("Please wait for your opponent")
            self.rightWidget.commandPanel.clear()
            return
        
        match self.main_flow_status:
            # case Bot_flow_status.setting_status:
            #     if input == "computer":
            #         self.playWithComputerHandler()
            #         self.rightWidget.commandPanel.clear()
            #         return
            #     elif input == "online":
            #         self.playWithOtherButtonHandler()
            #         self.rightWidget.commandPanel.clear()
            #         return
            case Bot_flow_status.select_status:
                if input.count("+"):
                    minute = input.split("+")[0]
                    increment = input.split("+")[1]
                    print(f"minute = {minute}, inc = {increment}")

            case Bot_flow_status.board_init_status:
                return
            case Bot_flow_status.game_play_status:
                if input.count("color"):
                    speak("You are playing as {}".format(self.userColor))
                    return
                if input.count("time") or input == "t":
                    if self.game_play_mode == Game_play_mode.online_mode:

                        def timeCallback(clocks):
                            if not clocks == None:
                                user_time = clocks[1].split(":")
                                user = (
                                    user_time[0]
                                    + " minutes "
                                    + user_time[1]
                                    + " seconds"
                                )

                                opponent_time = clocks[0].split(":")
                                opponent = (
                                    opponent_time[0]
                                    + " minutes "
                                    + opponent_time[1]
                                    + " seconds"
                                )
                                speak(
                                    Speak_template.check_time_sentense.value.format(
                                        user, opponent
                                    )
                                )

                        self.leftWidget.checkTime(timeCallback)
                        self.rightWidget.commandPanel.clear()
                        return
                    else:
                        speak("No timer for computer mode")
                        self.rightWidget.commandPanel.clear()
                        return
                if input.count("resign"):
                    self.resign_handler()
                    self.rightWidget.commandPanel.clear()
                    return
                if input.count("where"):
                    piece_type = input.replace("where", "").replace(" ", "")
                    try:
                        piece_type = PIECE_TYPE_CONVERSION[piece_type]
                    except Exception as e:
                        print(e)
                    grid = self.chessBoard.check_piece(piece_type)
                    speak_string = ""
                    white = grid["WHITE"]
                    if len(white) > 0:
                        speak_string = (
                            speak_string
                            + len(white).__str__()
                            + " WHITE "
                            + piece_type
                            + white.__str__().upper()
                        )
                    else:
                        speak_string = speak_string + "NO WHITE " + piece_type

                    speak_string = speak_string + " and "
                    black = grid["BLACK"]
                    if len(white) > 0:
                        speak_string = (
                            speak_string
                            + len(black).__str__()
                            + " BLACK "
                            + piece_type
                            + black.__str__().upper()
                        )
                    else:
                        speak_string = speak_string + "NO BLACK " + piece_type
                    # speak(piece_type + " " + grid.__str__())
                    speak(speak_string)
                    self.rightWidget.commandPanel.clear()
                    return
                elif input.count("what"):
                    grid = input.replace("what", "").replace(" ", "")
                    piece = self.chessBoard.check_grid(grid).__str__()
                    speak_sentence = grid.upper()

                    print(piece)
                    if not piece == "Invalid square name":
                        if not piece == "None":
                            if piece.__str__().islower():
                                speak_sentence = speak_sentence + " BLACK "
                            else:
                                speak_sentence = speak_sentence + " WHITE "
                            speak(
                                speak_sentence
                                + PIECE_TYPE_CONVERSION[piece.__str__().lower()]
                            )
                        else:
                            speak(speak_sentence + " empty")
                    else:
                        speak(speak_sentence)
                    self.rightWidget.commandPanel.clear()
                    return
                if self.game_flow_status == Game_flow_status.user_turn:
                    self.movePiece(input)
                else:
                    speak("Please wait for your opponent's move")
    
    def movePiece(self, input):  ## input store the move command

        movePair = self.chessBoard.moveWithValidate(input)
        # check_win = self.chessBoard.detect_win()

        print(self.chessBoard.board_object)
        san_string = ""
        uci_string = ""
        human_string = ""
        if len(movePair) == 2:
            uci_string = movePair[0]
            san_string = movePair[1]
            human_string = self.move_to_human_form(
                self.userColor, uci_string, san_string
            )

            # movePair = movePair[0]

        if len(uci_string) == 5:
            self.moveList.append(uci_string)  ## record move

            target = uci_string[:2]
            dest = uci_string[2:4]
            promoteTo = (
                san_string[san_string.index("=") + 1].__str__().lower()
            )
            promote_index = list(PIECE_TYPE_CONVERSION).index(promoteTo)

            # dlg = confirmMoveDialog("pawn", dest, promote=promoteTo)
            dlg = confirmDialog(human_string)
            if dlg.exec():
                self.all_grids_switch(False)
                targetWidget = self.leftWidget.grids[target]
                destWidget = self.leftWidget.grids[dest]
                if widgetDragDrop(targetWidget, destWidget):
                    match self.userColor:
                        case "BLACK":
                            place = str(dest[0]) + str(
                                int(dest[1]) + promote_index
                            )
                        case "WHITE":
                            place = str(dest[0]) + str(
                                int(dest[1]) - promote_index
                            )
                    promoteWidget = self.leftWidget.grids[place]
                    if widgetClick(promoteWidget):
                        self.rightWidget.commandPanel.clear()
                        QTimer.singleShot(1000, self.focus_back)
                        self.getOpponentMoveTimer.start(1000)
            else:
                self.chessBoard.board_object.pop()
                self.rightWidget.commandPanel.clear()
                print("Cancel!")

        elif len(uci_string) == 4:
            self.moveList.append(uci_string)    ## record move

            target = uci_string[:2]

            dest = uci_string[2:4]
            target_type = PIECE_TYPE_CONVERSION.get(
                self.chessBoard.check_grid(dest).__str__().lower()
            )
            # dlg = confirmMoveDialog(target_type, dest)
            dlg = confirmDialog(human_string)
            if dlg.exec():
                self.all_grids_switch(False)
                # QTimer.singleShot(3000, partial(self.clickStart,input))
                # print(self.chessBoard.board_object)

                targetWidget = self.leftWidget.grids[target]
                destWidget = self.leftWidget.grids[dest]
                self.rightWidget.commandPanel.clear()
                if widgetDragDrop(targetWidget, destWidget):
                    QTimer.singleShot(1000, self.focus_back)
                    self.getOpponentMoveTimer.start(1000)
            else:
                self.chessBoard.board_object.pop()
                self.rightWidget.commandPanel.clear()
                print("Cancel!")
        elif movePair == "Promotion":
            print("Promotion")
            speak(
                "Please indicate the promotion piece by typing the first letter"
            )
            self.rightWidget.commandPanel.setFocus()
        else:
            speak(input + movePair)
            print(input + movePair)  ##error move speak
            self.rightWidget.commandPanel.clear()

    ##check game end, sync with mirrored chess board and announce opponent's move
    def announceMove(self, sanString):
        print("broadcast move: ", sanString)
        if sanString == None or self.chessBoard == None:
            return False
        crawl_result = None
        check_win = self.chessBoard.detect_win()
        if not check_win == "No win detected.":  ##check user wins
            print(check_win)
            speak(check_win)
            self.game_flow_status = Game_flow_status.game_end
            self.change_main_flow_status(Bot_flow_status.setting_status)
            self.getOpponentMoveTimer.stop()
            self.getScoreTimer.start(1000)
            return True
        
        print("check none ")
        if sanString != None:
            print(sanString)
            movePair = self.chessBoard.moveWithValidate(sanString)
            if not len(movePair) == 2:
                if not crawl_result == None:
                    self.game_flow_status = Game_flow_status.game_end
                    self.change_main_flow_status(Bot_flow_status.setting_status)
                    self.getOpponentMoveTimer.stop()
                    self.getScoreTimer.start(1000)
                    speak(crawl_result, True)
                    return True
                else:
                    return False
            uci_string = movePair[0]
            san_string = movePair[1]

            print(self.chessBoard.board_object)
            if len(uci_string) <= 5:
                human_string = self.move_to_human_form(
                    self.opponentColor, uci_string, san_string
                )

                check_win = self.chessBoard.detect_win()
                print(check_win)
                print(crawl_result)
                speak(
                    human_string,
                    importance=True,
                )
                self.rightWidget.opponentBox.setText(
                    "Opponent move: \n" + human_string
                )
                self.game_flow_status = Game_flow_status.user_turn
                if not check_win == "No win detected.":
                    speak(check_win, True)
                    self.game_flow_status = Game_flow_status.game_end
                    self.change_main_flow_status(Bot_flow_status.setting_status)
                    self.getOpponentMoveTimer.stop()
                    self.getScoreTimer.start(1000)
                if not crawl_result == None:
                    self.game_flow_status = Game_flow_status.game_end
                    self.change_main_flow_status(Bot_flow_status.setting_status)
                    self.getOpponentMoveTimer.stop()
                    self.getScoreTimer.start(1000)
                    speak(crawl_result, True)
                return True
        
        return False

    ##Check whether opponent resigned
    def check_game_end(self):
        def callback(x):
            win_move = None
            win_index = None
            reason = None
            if x == "game end":
                    self.game_flow_status = Game_flow_status.game_end
                    self.change_main_flow_status(Bot_flow_status.setting_status)
                    self.getScoreTimer.start(1000)
                    self.getOpponentMoveTimer.stop()
                    print("game end")
                    speak("game end")
         
        if(self.userColor=="WHITE"):
            jsCode = js_function.white_GetOpponentMove
        else:
            jsCode = js_function.black_GetOpponentMove

        self.leftWidget.chessWebView.page().runJavaScript(jsCode, callback)

    ##JS to get opponent move SAN
    def getOpponentMove(self):
        def callback(x):

            print(f"Opponent move = {x}")
            
            if self.announceMove(x):
                self.getOpponentMoveTimer.stop()
            else:
                self.getOpponentMoveTimer.start(1000)

        if(self.userColor=="WHITE"):
            jsCode = js_function.white_GetOpponentMove
        else:
            jsCode = js_function.black_GetOpponentMove
        if self.input_mode == Input_mode.arrow_mode:
            self.all_grids_switch(True)

        self.game_flow_status = Game_flow_status.opponent_turn

        self.leftWidget.chessWebView.page().runJavaScript(jsCode, callback)

    ##JS to click on web view button
    def clickWebButton(
        self, displayTextList, index, finalCallback, retry
    ):  ##avoid double load finish
        if index >= len(displayTextList):
            print("click finished")
            # QTimer.singleShot(1000, finalCallback)
            finalCallback()
            # self.capture_screens
            # hot()
            return True

        def next_click(result):
            if result == displayTextList[index][1].lower() or retry >= 6:
                QTimer.singleShot(
                    1000,
                    partial(
                        self.clickWebButton,
                        displayTextList,
                        index + 1,
                        finalCallback,
                        0,
                    ),
                )
            else:
                ## retry
                add = retry + 1
                QTimer.singleShot(
                    500,
                    partial(
                        self.clickWebButton, displayTextList, index, finalCallback, add
                    ),
                )

        # print(displayTextList[index][0], displayTextList[index][1].lower())
        if len(displayTextList[index]) == 3:
            jsCode = """
            function out() {{
                let buts = document.querySelectorAll('{0}');
                for(but of buts){{
                    if(but?.textContent?.trim()?.toLowerCase()=='{1}'||but?.innerText?.trim()?.toLowerCase() == '{1}'){{
                        but.click();
                        console.error(but?.textContent)
                        console.error("**********************************")
                        console.error('{1}')
                        console.error("**********************************")
                        return '{1}';
                    }}
                }}
                return false;
            }}
            out();
            """.format(
                displayTextList[index][0], displayTextList[index][1].lower()
            )
        else:
            jsCode = """
                function out() {{
                    let buts = document.querySelectorAll('{0}');
                    for(but of buts){{
                        if(but?.textContent?.trim()?.toLowerCase().includes('{1}')||but?.innerText?.trim()?.toLowerCase().includes('{1}')){{
                            but.click();
                            console.error(but?.textContent)
                            console.error("**********************************")
                            console.error('{1}')
                            console.error("**********************************")
                            return '{1}';
                        }}
                    }}
                    return false;
                }}
                out();
                """.format(
                displayTextList[index][0], displayTextList[index][1].lower()
            )
        return self.leftWidget.chessWebView.page().runJavaScript(jsCode, next_click)

    ##assign square after detect the web view chessboard and color
    def getBoard(self, *args):
        for row in range(8):
            for col in range(8):
                self.leftWidget.grids[self.alphabet[col] + self.number[row]] = (
                    self.leftWidget.grids.pop(row.__str__() + col.__str__())
                )
                self.leftWidget.grids[
                    self.alphabet[col] + self.number[row]
                ].setAccessibleName(self.alphabet[col] + self.number[row])

        self.chessBoard = ChessBoard(args[0]) if(args) else ChessBoard()
        self.change_main_flow_status(Bot_flow_status.game_play_status)

    ##toggle the marked square layer -> hide before perfrom click
    def all_grids_switch(self, on_off):
        for grid in self.leftWidget.grids.values():
            if on_off:
                grid.show()
            else:
                grid.hide()

    ##computer vision to detect the chessboard
    def initBoard(self, retry=0):
        if retry > 3:
            speak("board detection error, retry initialize", True)
            if self.game_play_mode == Game_play_mode.computer_mode:
                self.playWithComputerHandler()
            elif(self.game_play_mode == Game_play_mode.online_mode):
                self.playWithOtherButtonHandler()
            return
        
        x = None
        try:
            file_path = os.path.join(current_dir, "Tmp", "board_screenshot.png")
            # file_path = "./widget_screenshot.png"
            screenshot = self.leftWidget.chessWebView.grab()
            screenshot.save(file_path)
            print("cap here")
            viewWidth = self.leftWidget.chessWebView.width()
            viewHeight = self.leftWidget.chessWebView.height()
            x, y, w, h = detectChessboard(file_path, viewWidth, viewHeight)
        except Exception as e:
            print("error retry", e)
            retry = retry + 1
            # QTimer.singleShot(2000, partial(self.initBoard, retry))
                
        self.board_x = int(x)
        self.board_y = int(y)
        self.board_w = int((w / 8))
        self.board_h = int((h / 8))
        print(f"x: {self.board_x}, y: {self.board_y}, w: {self.board_w}, h: {self.board_h}")

        for row in range(8):
            for col in range(8):
                label = QLabel(self.leftWidget)
                label.setGeometry(self.board_x + col * self.board_w, self.board_y + row * self.board_h, self.board_w, self.board_h)
                # if (row + col) % 2 == 0:
                #     label.setStyleSheet("background-color: rgba(0, 0, 255, 100);")
                # else:
                #     label.setStyleSheet("background-color: rgba(255, 0, 0, 100);")
                self.leftWidget.grids[row.__str__() + col.__str__()] = label
                label.show()
                # label.hide()  # comment this to check whether the board detect success
        
    def getColor(self):
        user_rook_file = os.path.join(current_dir, "Tmp", "color_detection_user.png")

        user_rook = self.leftWidget.grids["77"]

        self.leftWidget.chessWebView.grab(
            QRect(user_rook.x(), user_rook.y(), self.board_w, self.board_h)
        ).save(user_rook_file)

        color = userColor(user_rook_file)
        self.userColor = color
        self.rightWidget.colorBox.setText("Assigned Color: " + color)
        if color == "BLACK":
            self.opponentColor = "WHITE"
            self.alphabet.reverse()
            speak(Speak_template.user_black_side_sentense.value)
            self.game_flow_status = Game_flow_status.opponent_turn
            self.getOpponentMoveTimer.start(1000)
        else:
            self.opponentColor = "BLACK"
            self.number.reverse()
            speak(Speak_template.user_white_side_sentense.value)
            self.game_flow_status = Game_flow_status.user_turn

    ##switch to command mode
    def switch_command_mode(self):
        print("shortcut ctrl + F pressed")
        speak("command mode <> you can type your move here")
        self.arrow_mode_switch(False)
        self.input_mode = Input_mode.command_mode
        self.currentFoucs = len(self.rightWidget.play_menu)
        self.rightWidget.commandPanel.setFocus()

    ##switch to arrow mode, only allowd when game started
    def switch_arrow_mode(self):
        print("shortcut ctrl + J pressed")
        if self.main_flow_status == Bot_flow_status.game_play_status:

            speak("arrow_mode")
            self.input_mode = Input_mode.arrow_mode
            self.arrow_mode_switch(True)
            self.all_grids_switch(True)
            self.rightWidget.commandPanel.clear()

            self.leftWidget.setStyleSheet(
                "QLabel:focus { border: 5px solid rgba(255, 0, 0, 1); }"
            )
            init_focus = self.alphabet[0].__str__() + self.number[-1].__str__()
            self.leftWidget.grids[init_focus].setFocus()
            self.currentFoucs = init_focus

    ##arrow key move and speak the square information
    def handle_arrow(self, direction):
        if not self.main_flow_status == Bot_flow_status.game_play_status:
            return
        file = self.currentFoucs[0]
        rank = self.currentFoucs[1]

        alphabet_index = self.alphabet.index(file)
        number_index = self.number.index(rank)
        # print(self.currentFoucs, direction)
        match direction:
            case "UP":
                num = max(number_index - 1, 0)
                self.leftWidget.grids[file + self.number[num]].setFocus()
                self.currentFoucs = file + self.number[num]
            case "DOWN":
                num = min(number_index + 1, 7)
                self.leftWidget.grids[file + self.number[num]].setFocus()
                self.currentFoucs = file + self.number[num]
            case "LEFT":
                alp = max(alphabet_index - 1, 0)
                self.leftWidget.grids[self.alphabet[alp] + rank].setFocus()
                self.currentFoucs = self.alphabet[alp] + rank
            case "RIGHT":
                alp = min(alphabet_index + 1, 7)
                self.leftWidget.grids[self.alphabet[alp] + rank].setFocus()
                self.currentFoucs = self.alphabet[alp] + rank
        # QLabel.setAccessibleDescription("HELLO")
        # QLabel.setAccessibleName("Name")
        piece = self.chessBoard.check_grid(self.currentFoucs).__str__()
        if piece == "None":
            speak("{0}".format(self.currentFoucs.upper()))
            return
        else:
            color = "white" if piece.isupper() else "black"
            piece_square_text = "{0} {1} {2}".format(
                self.currentFoucs.upper(),
                color,
                PIECE_TYPE_CONVERSION.get(piece.lower()),
            )
            print(piece_square_text)
            speak(piece_square_text)
            self.leftWidget.grids[self.currentFoucs].setAccessibleDescription(
                piece_square_text
            )

    ##select the piece under arrow mode
    def handle_space(self):
        if not self.input_mode == Input_mode.arrow_mode:
            return
        if len(self.rightWidget.commandPanel.text()) == 4:
            self.CommandPanelHandler()
            return
        if not self.currentFoucs == None:
            piece = self.chessBoard.check_grid(self.currentFoucs).__str__()
            if not piece == "None":
                color = "white" if piece.isupper() else "black"
                piece = PIECE_TYPE_CONVERSION.get(piece.lower())
                speak(color + " " + piece + " selected")

        current_value = self.rightWidget.commandPanel.text()
        self.rightWidget.commandPanel.setText(current_value + self.currentFoucs)
        if len(self.rightWidget.commandPanel.text()) == 4:
            self.CommandPanelHandler()

    ##clear the selected piece under arrow mode
    def handle_arrow_delete(self):
        if not self.input_mode == Input_mode.arrow_mode:
            return
        self.rightWidget.commandPanel.setText("")

    ##control tab event on right widget
    def handle_tab(self):
        print("tab")
        if self.input_mode == Input_mode.command_mode:
            unhidden_widgets = []
            layout = self.rightWidget.layout()
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget and not widget.isHidden():
                    unhidden_widgets.append(widget)
            if int(self.currentFoucs + 1) >= len(unhidden_widgets):
                unhidden_widgets[0].setFocus()
                self.currentFoucs = 0
            else:
                unhidden_widgets[self.currentFoucs + 1].setFocus()
                self.currentFoucs = self.currentFoucs + 1

            intro = unhidden_widgets[self.currentFoucs].text()
            if intro == "":
                intro = unhidden_widgets[self.currentFoucs].accessibleDescription()
            # speak(intro)
        else:
            self.leftWidget.grids[self.currentFoucs].setFocus()

    ##switch to arrow mode
    def arrow_mode_switch(self, on_off):
        arrows = ["UP", "DOWN", "LEFT", "RIGHT", "SPACE", "DELETE"]
        for arrow in arrows:
            self.all_shortcut.get(arrow).setEnabled(on_off)

    ##repeat the previous sentence
    def repeat_previous(self):
        speak(previous_sentence)

    ##tell user different options based on the application status
    def helper_menu(self):
        print("helper")
        match self.main_flow_status:
            case Bot_flow_status.setting_status:
                speak(Speak_template.setting_state_help_message.value)
                return
            case Bot_flow_status.board_init_status:
                speak(Speak_template.init_state_help_message.value)
                return
            case Bot_flow_status.game_play_status:
                if self.input_mode == Input_mode.command_mode:
                    sentence = Speak_template.command_panel_help_message.value
                    # if self.game_play_mode == Game_play_mode.online_mode:
                    #     sentence = (
                    #         + Speak_template.command_panel_help_message.value
                    #     )

                    speak(sentence)
                elif self.input_mode == Input_mode.arrow_mode:
                    speak(
                        Speak_template.arrow_mode_help_message.value
                        + "or press control F for command mode"
                    )

    def __init__(self, *args, **kwargs):
        
        global previous_sentence

        self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.number = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.chess_position = [a + b for a in [x.lower() for x in self.alphabet] for b in self.number]
        self.moveList = []
        self.FenNotation = ""
        self.previous_game_exist = False
        self.boardDescription = []

        super(MainWindow, self).__init__(*args, **kwargs)

        shortcut_F = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_F.activated.connect(self.switch_command_mode)

        shortcut_J = QShortcut(QKeySequence("Ctrl+J"), self)
        shortcut_J.activated.connect(self.switch_arrow_mode)

        shortcut_S = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_S.activated.connect(self.voice_input)

        shortcut_UP = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        shortcut_UP.activated.connect(partial(self.handle_arrow, "UP"))

        shortcut_DOWN = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        shortcut_DOWN.activated.connect(partial(self.handle_arrow, "DOWN"))

        shortcut_LEFT = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_LEFT.activated.connect(partial(self.handle_arrow, "LEFT"))

        shortcut_RIGHT = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_RIGHT.activated.connect(partial(self.handle_arrow, "RIGHT"))

        shortcut_SPACE = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        shortcut_SPACE.activated.connect(self.handle_space)

        shortcut_DELETE = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self)
        shortcut_DELETE.activated.connect(self.handle_arrow_delete)

        shortcut_TAB = QShortcut(QKeySequence(Qt.Key.Key_Tab), self)
        shortcut_TAB.activated.connect(self.handle_tab)

        shortcut_F1 = QShortcut(QKeySequence("Ctrl+1"), self)
        shortcut_F1.activated.connect(self.playWithComputerHandler)

        shortcut_F2 = QShortcut(QKeySequence("Ctrl+2"), self)
        shortcut_F2.activated.connect(self.playWithOtherButtonHandler)

        shortcut_F3 = QShortcut(QKeySequence("Ctrl+3"), self)
        shortcut_F3.activated.connect(self.puzzleModeHandler)

        shortcut_R = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_R.activated.connect(self.repeat_previous)

        shortcut_O = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_O.activated.connect(self.helper_menu)

        shortcut_z = QShortcut(QKeySequence("z"), self)
        shortcut_z.activated.connect(self.stockfish_adviser_caller)

        shortcut_x = QShortcut(QKeySequence("x"), self)
        shortcut_x.activated.connect(lambda: print(f"current game flow status: {self.game_flow_status}"))

        shortcut_c = QShortcut(QKeySequence("c"), self)
        shortcut_c.activated.connect(lambda: print(f"current main flow status: {self.main_flow_status}"))

        shortcut_a = QShortcut(QKeySequence("a"), self)
        shortcut_a.activated.connect(self.analysis)
        
        self.all_shortcut = {
            "F": shortcut_F,
            "J": shortcut_J,
            "UP": shortcut_UP,
            "DOWN": shortcut_DOWN,
            "LEFT": shortcut_LEFT,
            "RIGHT": shortcut_RIGHT,
            "SPACE": shortcut_SPACE,
            "DELETE": shortcut_DELETE,
        }

        self.arrow_mode_switch(False)
        ##initialize flow status
        self.main_flow_status = Bot_flow_status.setting_status
        self.game_flow_status = Game_flow_status.not_start
        self.input_mode = Input_mode.command_mode
        self.game_play_mode = None

        ##initialize UI components
        self.mainWidget = QWidget()
        self.leftWidget = LeftWidget()
        self.rightWidget = RightWidget()

        ##initialize stockfish component for chess move advice 
        self.stockfish = stockfish_adviser()

        def timeCallback(clocks):
            if not clocks == None:
                user_time = clocks[1].split(":")
                user = user_time[0] + " minutes " + user_time[1] + " seconds"

                opponent_time = clocks[0].split(":")
                opponent = (
                    opponent_time[0] + " minutes " + opponent_time[1] + " seconds"
                )
                speak(Speak_template.check_time_sentense.value.format(user, opponent))

        self.rightWidget.check_time.clicked.connect(
            partial(self.leftWidget.checkTime, timeCallback)
        )
        self.rightWidget.playWithComputerButton.clicked.connect(
            self.playWithComputerHandler
        )
        self.rightWidget.playWithOtherButton.clicked.connect(
            self.playWithOtherButtonHandler
        )

        self.rightWidget.puzzleModeButton.clicked.connect(
            self.puzzleModeHandler
        )

        self.rightWidget.resign.clicked.connect(self.resign_handler)

        self.rightWidget.commandPanel.returnPressed.connect(self.CommandPanelHandler)
        self.rightWidget.check_position.returnPressed.connect(
            self.check_position_handler
        )

        self.rightWidget.selectPanel.returnPressed.connect(self.selectPanelHandler)

        self.leftWidget.chessWebView.loadFinished.connect(self.leftWidget.checkLogined)

        self.leftWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.getScoreTimer = QTimer()
        self.getScoreTimer.timeout.connect(self.check_score)

        self.getOpponentMoveTimer = QTimer()
        self.getOpponentMoveTimer.timeout.connect(self.getOpponentMove)

        self.check_game_end_timer = QTimer()
        self.check_game_end_timer.timeout.connect(self.check_game_end)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.leftWidget)
        mainLayout.addWidget(self.rightWidget)
        self.mainWidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainWidget)

        self.chessBoard = None
        self.userColor = None
        self.opponentColor = None
        ##need to modify /Users/longlong/miniforge3/envs/fyp/lib/python3.12/site-packages/pyttsx3/drivers/nsss.py
        ## import objc and self.super
        self.rightWidget.playWithComputerButton.setFocus()
        self.currentFoucs = 0
        # self.show_information_box()

        self.rightWidget.playWithOther_Bullet_1_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_1_0.value))
        self.rightWidget.playWithOther_Bullet_1_1_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_1_1.value))
        self.rightWidget.playWithOther_Bullet_2_1_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_2_1.value))

        self.rightWidget.playWithOther_Blitz_3_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_3_0.value))
        self.rightWidget.playWithOther_Blitz_3_2_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_3_2.value))
        self.rightWidget.playWithOther_Blitz_5_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_5_0.value))

        self.rightWidget.playWithOther_Rapid_10_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_10_0.value))
        self.rightWidget.playWithOther_Rapid_15_10_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_15_10.value))
        self.rightWidget.playWithOther_Rapid_30_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_30_0.value))

        voice_input_thread.action_signal.connect(self.voice_action)

    def analysis(self):
        def setMoveLength(length):
            self.moveLength = length
            print(f"moveLength = {self.moveLength}")

        def callback1(x):
            QTimer.singleShot(500, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.getGameId, callback2))

        def callback2(gameId):
            print(gameId)
            self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(5000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.checkReviewLimited, callback3)))
            if(self.game_play_mode == Game_play_mode.computer_mode):
                self.leftWidget.chessWebView.load(QUrl(f"https://www.chess.com/analysis/game/computer/{gameId}"))
            else:
                self.leftWidget.chessWebView.load(QUrl(f"https://www.chess.com/analysis/game/live/{gameId}"))

        def callback3(ReviewLimited):
            self.leftWidget.chessWebView.loadFinished.disconnect()
            if(ReviewLimited):
                print("You have used your free Game Review for the day.")
            else:
                self.leftWidget.key_signal.connect(self.analysisAction)
                self.leftWidget.chessWebView.page().runJavaScript(js_function.clickStartReview, callback4)
                self.game_play_mode = Game_play_mode.analysis_mode

        def callback4(comment):
            QTimer.singleShot(300, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.getMoveLength, setMoveLength))
            self.gameReviewMode_Reader(comment)

        # if(self.game_flow_status != Game_flow_status.game_end):
        #     print("No finished game for analysis")
        #     return
        self.bestExist = False
        self.analysisCount = 0
        self.analysisBoard = ChessBoard()
        self.keyPressed = None
        self.moveLength = -1
        self.leftWidget.chessWebView.page().runJavaScript(js_function.clickGameReview, callback1)
        
    def gameReviewMode_Reader(self, comment):
        print(comment)
        if(isinstance(comment, list)):
            self.feedback = comment[0]
            self.explain = comment[1]
            self.bestExist = comment[2]
            print(self.keyPressed)
            print(f"analysis Count: {self.analysisCount}")
            if(self.keyPressed == keyPressed.leftArrow):
                if(self.analysisCount==0):
                    self.analysisBoard.board_object.pop()
                else:
                    self.analysisBoard.board_object.pop()
                    self.analysisBoard.board_object.pop()

            sanString = self.feedback.split(" ")[0].strip()
            print(f"feedback: {self.feedback}")
            self.feedback = self.feedback.replace(sanString, self.analysisHumanForm(self.feedback))

            self.keyPressed = None
        else:
            if(self.keyPressed == keyPressed.leftArrow):
                self.analysisBoard.board_object.pop()
            self.feedback = comment

        print(self.analysisBoard.board_object)
        print(self.feedback)
        speak(self.feedback)

    def gameReviewMode_Explainer(self):
        print(self.explain)
        speak(self.explain)

    def getReviewComment(self):
        self.leftWidget.chessWebView.page().runJavaScript(js_function.getReviewComment, self.gameReviewMode_Reader)

    def analysisAction(self, key):
        if(self.game_play_mode == Game_play_mode.analysis_mode):
            match key:
                case Qt.Key.Key_Left:
                    self.keyPressed = keyPressed.leftArrow
                    if(self.analysisCount == 0):
                        speak("This is the beginning")
                    else:
                        self.analysisCount -= 1
                        QTimer.singleShot(300, self.getReviewComment)
                        
                case Qt.Key.Key_Right:
                    self.keyPressed = keyPressed.rightArrow
                    if(self.analysisCount == self.moveLength):
                        speak("This the last move")
                    else:
                        self.analysisCount += 1
                        QTimer.singleShot(300, self.getReviewComment)

                case Qt.Key.Key_Up:
                    self.keyPressed = keyPressed.upArrow
                    self.analysisCount = 0
                    self.analysisBoard = ChessBoard()
                    print(self.analysisBoard)
                    QTimer.singleShot(300, self.getReviewComment)

                case Qt.Key.Key_Down:
                    self.keyPressed = keyPressed.downArrow
                    # QTimer.singleShot(300, self.getReviewComment)

                case Qt.Key.Key_E:
                    self.gameReviewMode_Explainer()

                case Qt.Key.Key_B:
                    if(self.bestExist):
                        self.keyPressed = keyPressed.keyB
                        self.leftWidget.chessWebView.page().runJavaScript(js_function.getBestMove)
                        self.poppedMove = self.analysisBoard.board_object.pop()
                        QTimer.singleShot(1000, self.getReviewComment)

    def analysisHumanForm(self, move):
        sanString = move.split(" ")[0].strip()
        uciString = str(self.analysisBoard.board_object.parse_san(sanString))
        en_passant = self.analysisBoard.board_object.has_legal_en_passant()
        srcLocation = uciString[:2]
        destLocation = uciString[2:4]

        src = self.analysisBoard.parseSquare(srcLocation)
        dest = self.analysisBoard.parseSquare(destLocation)
        result = ""

        src_piece_type = self.analysisBoard.board_object.piece_at(src)
        dest_piece_type = self.analysisBoard.board_object.piece_at(dest)
        srcPiece = PIECES_SHORTFORM_CONVERTER[str(src_piece_type)]
        if(dest_piece_type is not None):
            destPiece = PIECES_SHORTFORM_CONVERTER[str(dest_piece_type)]
        
        if sanString.count("x"):
            if(en_passant and str(src_piece_type).lower() == "p" and dest_piece_type is None):
                result = (f"{srcPiece} on {srcLocation} capture pawn on {uciString[2]+uciString[1]} by en passant")
            else:
                result = (f"{srcPiece} on {srcLocation} captures {destPiece} on {destLocation}")
        elif sanString.count("O-O-O"):
            result = "Queenside castling"
        elif sanString.count("O-O"):
            result = "Kingside castling"
        else:
            result = (f"{srcPiece} on {srcLocation} moves to {destLocation}")
        
        if(sanString.count("=")):
            result += f" then promoted to {PIECES_SHORTFORM_CONVERTER[uciString[4]]}"

        if(self.keyPressed == keyPressed.keyB):
            self.analysisBoard.board_object.push(self.poppedMove)
        else:
            self.analysisBoard.board_object.push_san(sanString)
        return result
                
    def voice_input(self):
        print("Ctrl S is pressed")
        voice_input_thread.activate = not voice_input_thread.activate
        if voice_input_thread.activate:
            print("Voice Input activated. Listening...")

    def voice_action(self, str):
        match(str):
            case "options":
                self.helper_menu()
            case "computer":
                self.playWithComputerHandler()
            case "online":
                self.playWithOtherButtonHandler()
            case "puzzle":
                self.puzzleModeHandler()
            case "move":
                if self.game_play_mode == Game_play_mode.puzzle_mode:
                    self.puzzle_movePiece()
                else:
                    self.movePiece(voice_input_thread.chess_move)
            case "resign":
                self.resign_handler()

    def stockfish_adviser_caller(self):
        if(self.main_flow_status == Bot_flow_status.game_play_status):
            if(self.game_flow_status == Game_flow_status.user_turn):
                with open("./stockfishTicket.txt", "r") as file:
                    self.stockfishTicket = int(file.read())
                if(not self.stockfishTicket == 0):
                    suggestion = self.stockfish.suggested_move(self.chessBoard.current_board())
                    with open("./stockfishTicket.txt", "w+") as file:                    
                        file.write(str(self.stockfishTicket - 1))
                        file.seek(0)
                        print(f"ticket left: {file.read()}")
                    print(suggestion)
                    speak(suggestion)
                else:
                    print("You have already used all chances for advice!")
            else:
                print("Please wait for opponent finish their move")
        else:
            print("You are not playing any chess game")

    def currentOption(self):
        match self.main_flow_status:
            case Bot_flow_status.setting_status:
                print("Choose the game mode that you want to play")


    
## load text to TTS queue
def speak(sentence, importance=False, dialog=False):
    global previous_sentence
    global internal_speak_engine

    previous_sentence = sentence
    if internal_speak_engine:
        speak_thread.queue.put((sentence, importance))
    else:
        print("no speak engine")

class VoiceInput_Thread(QThread):
    '''
    Allow User using Voice Input by record user's audio, perform Speech to Text and
    determine which action to perform based on the text result
    '''

    action_signal = pyqtSignal(str)
    activate_signal = pyqtSignal()

    ##auto start and loop until application close
    def __init__(self):
        super(VoiceInput_Thread, self).__init__()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("base.en", device=device)
        
        self.audio_input = "test.wav"
        self.text_output = ""
        self.activate = False
        self.daemon = True
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK)
        self.frames = []
        self.chess_move = []
        self.activate_signal.connect(self.run)
        self.start()

    def run(self):
        print("Voice Input function running")
        voiceInput_running = True
        while voiceInput_running:
            time.sleep(0.5)
            while self.activate:
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)
            if self.frames:
                print("Voice Input Ended")
                with wave.open("tmp.wav", 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(self.frames))
                self.frames=[]
                self.activate = False
                print("Speech to Text performing...")
                self.text_output = self.model.transcribe("movetest.wav", fp16=False)["text"].lower()
                print(f"Speech to Text finished! Output: {self.text_output}")
                self.checkAction()

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def checkAction(self):
        print(f"Current main_flow_status: {window.main_flow_status}")
        ##Check voice instruction
        if(any(words in self.text_output for words in determinant.quit_application_words.value)):
            sys.exit()

        if(any(words in self.text_output for words in determinant.options_words.value)):
            self.action_signal.emit("options")

        if(window.main_flow_status == Bot_flow_status.setting_status):
            if(any(words in self.text_output for words in determinant.computer_mode_words.value)):
                self.action_signal.emit("computer")

            elif(any(words in self.text_output for words in determinant.online_mode_words.value)):
                self.action_signal.emit("online")

            elif(any(words in self.text_output for words in determinant.puzzle_mode_words.value)):
                self.action_signal.emit("puzzle")

        elif(window.main_flow_status == Bot_flow_status.select_status):
            match window.game_play_mode:
                case Game_play_mode.computer_mode:
                    self.action_signal.emit()
                case Game_play_mode.online_mode:
                    for words in timeControl:
                        if(words.value in self.text_output):
                            self.action_signal.emit(words.value) 
                case Game_play_mode.puzzle_mode:
                    self.action_signal.emit()

        elif(window.main_flow_status == Bot_flow_status.game_play_status):
            match window.game_play_mode:
                case Game_play_mode.puzzle_mode:
                    self.voiceToMove()
                case _:
                    if(any(words in self.text_output for words in determinant.resign_words.value)):
                        self.action_signal.emit("resign")
                    else:
                        self.voiceToMove()
            
        else:
            print("Sorry, I don't understand your request. Please repeat it again")

    def voiceToMove(self):
        self.chess_move = []
        for moves in window.chess_position:
            if moves in self.text_output:
                self.chess_move.append(moves)
        print(f"chess move = {self.chess_move}")
        if(len(self.chess_move)==2):
            self.chess_move = "".join(self.chess_move[0] + self.chess_move[1])
            print("move triggered")
            self.action_signal.emit("move")
        else:
            speak("Invalid Input")

if __name__ == "__main__":
    global speak_thread
    global voice_input_thread
    global current_dir
    global previous_sentence
    previous_sentence = ""

    speak_thread = TTSThread()  #activate TTS module
    voice_input_thread = VoiceInput_Thread()  #activate S2T module

    current_dir = os.path.dirname(os.path.realpath(__file__))

    app = QApplication(sys.argv)
    app.setApplicationName("Chess Bot")

    window = MainWindow()

    global internal_speak_engine
    internal_speak_engine = window.rightWidget.screen_reader_checkBox.isChecked()

    icon = QIcon(os.path.join(current_dir, "Resource", "Logo", "chessBot_logo.png"))
    window.setWindowIcon(icon)

    window.show()

    window.leftWidget.chessWebView.page().setWebChannel(window.leftWidget.chessWebView.page().webChannel())
    window.leftWidget.chessWebView.page().setInspectedPage(window.leftWidget.chessWebView.page())

    def welcome_callback():
        speak(
            Speak_template.welcome_sentense.value
            + Speak_template.game_intro_sentense.value,
            True,
        )
        window.leftWidget.chessWebView.loadFinished.disconnect()

    window.leftWidget.chessWebView.loadFinished.connect(welcome_callback)           

    window.move(10, 10)
    # window.switch_arrow_mode()
    sys.exit(app.exec())
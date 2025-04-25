import sys
import os
import chess
from threading import Event
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
    QTextEdit,
    QSlider,
    QComboBox,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QTimer, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QIcon


import Components.js_function as js_function    ## header file
from Components.piece_move_component import widgetDragDrop, widgetClick
from Components.chess_validation_component import ChessBoard
from Components.speak_component import TTSThread
from Utils.enum_helper import (
    Input_mode,
    Bot_flow_status,
    Game_flow_status,
    Speak_template,
    Game_play_mode,
    determinant,
    coach, adaptive, beginner, intermediate, advanced, master, athletes, musicians, creators, top_players, personalities, engine,
    timeControl,
    timeControlDeterminant_Type,
    timeControlDeterminant_Speak,
    chatbot_response,
)

import pyaudio
import wave
import whisper
import torch

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
        # self.chessWebView.setFixedSize(1000, 550)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.chessWebView)
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlayout)

        self.grids = [[0 for x in range(8)] for y in range(8)]

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
    
    # def keyPressEvent(self, event):
    #     self.key_signal.emit(event.key())

class CheckBox(QCheckBox):
    """
    CheckBox class that allowd check by enter
    """

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.nextCheckState()
        super(CheckBox, self).keyPressEvent(event)

# Simple Chatbot with pre-defined sentence and keywords to handle users' questions and requests
class ChatbotWindow(QMainWindow):
    """
    This class respresent the ChatBot widget.\n
    It contains the ChatBot interface and the functions to answer questions and handle operations.
    """
    action_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Chatbot")
        self.setMinimumSize(500, 500)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        #Detect current selecting button
        self.isInputArea = True

        # Create chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setDisabled(True)
        layout.addWidget(self.chat_display)

        # Create input area
        input_layout = QHBoxLayout()
        
        # Create message input
        self.message_input = QLineEdit()
        self.message_input.setAccessibleDescription("You can type your message here.")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        leaveButton = QPushButton("Leave")
        leaveButton.clicked.connect(self.hide)
        leaveButton.setAutoDefault(True)
        input_layout.addWidget(leaveButton)

        layout.addLayout(input_layout)

        self.message_input.returnPressed.connect(self.send_message)

        self.chatbotLayout = []
        self.chatbotLayout.append(self.message_input)
        self.chatbotLayout.append(leaveButton)

        # Welcome message
        self.chat_display.append("Chatbot: Hello! How can I help you today?")

        tab = QShortcut(QKeySequence("tab"), self)
        tab.activated.connect(self.tabHandler)

    def send_message(self):
        user_message = self.message_input.text().strip()
        if user_message:
            # Display user message
            self.chat_display.append(f"You: {user_message}")
            
            # Generate and display bot response
            bot_response = self.get_bot_response(user_message.lower())
            self.chat_display.append(f"Chatbot: {bot_response}")
            speak(bot_response)
            
            # Clear input field
            self.message_input.clear()

    def get_bot_response(self, message):
        # Simple response logic

    # Check for matching keywords
        for item in chatbot_response:
            for words in item.value:
                if(words in message):
                    return(item.value[words])

        for item in timeControlDeterminant_Type:
            for words in item.value:
                if (words in message):
                    print(f"Time Control: {item.value[words]}")
                    self.action_signal.emit(item.value[words])
                    self.hide()
                    return f"Starting a online player Game"

        # Default response
        return "I'm not sure how to respond to that. Try to ask other questions!"

    def tabHandler(self):
        self.isInputArea = not self.isInputArea
        print("tab")
        self.chatbotLayout[self.isInputArea].setFocus()
        intro = self.chatbotLayout[self.isInputArea].text()
        if(intro == ""):
            intro = self.chatbotLayout[self.isInputArea].accessibleDescription()
        speak(intro)

class CustomButton(QPushButton):
    def keyPressEvent(self, event):
        # Only ignore arrow keys for this button
        if event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
            event.ignore()
        else:
            super().keyPressEvent(event)
    

class SettingMenu(QDialog):
    def __init__(self, parent=None, rate=50, volume=0.7, engine=True):
        super().__init__(parent)
        
        # Set window title and size
        self.setWindowTitle("Settings")
        # self.setGeometry(200, 200, 400, 200)
        self.setMinimumSize(500, 500)
        
        # Create layout
        layout = QVBoxLayout()
        rate_layout = QHBoxLayout()
        volume_layout = QHBoxLayout()

        # Create checkbox
        self.engine_value = engine
        self.screen_reader_checkBox = QCheckBox("Enable internal speak engine")
        self.screen_reader_checkBox.setChecked(engine)
        self.screen_reader_checkBox.setAccessibleDescription(
            "Tick to use internal speak engine. Untick for important information announcement only."
        )
        layout.addWidget(self.screen_reader_checkBox)
        
        # Create slider
        self.rate_label = QLabel("Rate:")
        self.rate_label.setMinimumWidth(100)

        self.speech_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.speech_rate_slider.setMinimum(0)
        self.speech_rate_slider.setMaximum(100)
        self.speech_rate_slider.setValue(rate)
        self.speech_rate_slider.setTickPosition(QSlider.TickPosition.TicksRight)
        self.speech_rate_slider.setTickInterval(10)
        self.speech_rate_slider.setAccessibleName("Speech Rate")
        self.speech_rate_slider.setAccessibleDescription("Adjust the speech rate")

        self.speech_rate_value_label = QLabel()
        self.speech_rate_value_label.setText(str(rate))

        rate_layout.addWidget(self.rate_label)
        rate_layout.addWidget(self.speech_rate_slider)
        rate_layout.addWidget(self.speech_rate_value_label)


        self.volume_label = QLabel("Volume:")
        self.volume_label.setMinimumWidth(100)  # Set minimum width for consistent alignment

        self.speech_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.speech_volume_slider.setMinimum(0)
        self.speech_volume_slider.setMaximum(100)
        self.speech_volume_slider.setValue(volume)
        self.speech_volume_slider.setTickPosition(QSlider.TickPosition.TicksRight)
        self.speech_volume_slider.setTickInterval(10)
        self.speech_volume_slider.setAccessibleName("Volume")
        self.speech_volume_slider.setAccessibleDescription("Adjust the volume")

        self.volume_value_label = QLabel()
        self.volume_value_label.setText(str(volume))

        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.speech_volume_slider)
        volume_layout.addWidget(self.volume_value_label)

        # Connect slider value change to update label
        self.speech_rate_slider.valueChanged.connect(self.rate_changed)
        self.speech_volume_slider.valueChanged.connect(self.volume_changed)
        self.screen_reader_checkBox.stateChanged.connect(self.checkBoxStateChanged)
                
        layout.addLayout(rate_layout)
        layout.addLayout(volume_layout)
        
        # Create OK button to close the dialog
        ok_button = CustomButton("OK")
        ok_button.setAccessibleDescription("OK button")
        ok_button.clicked.connect(self.OK_pressed)
        layout.addWidget(ok_button)

        self.setting_layout = []
        self.setting_layout.append(self.screen_reader_checkBox)
        self.setting_layout.append(self.speech_rate_slider)
        self.setting_layout.append(self.speech_volume_slider)
        self.setting_layout.append(ok_button)
        
        # Set layout
        self.setLayout(layout)

        self.currentfocus = len(self.setting_layout) - 1

        tab = QShortcut(QKeySequence("tab"), self)
        tab.activated.connect(self.tabHandler)

    def checkBoxStateChanged(self, state):
        print(state)
        if state == 2:
            self.engine_value = True
            speak("Turn on speak engine")
        else:
            self.engine_value = False
            speak("Turn off speak engine")

    def get_engine_value(self):
        return self.engine_value

    def OK_pressed(self):
        speak("User Preference Saved")
        self.accept()

    def rate_changed(self, value):
        speak(value)
        self.speech_rate_value_label.setText(str(value))
    
    def volume_changed(self, value):
        speak(value)
        self.volume_value_label.setText(str(value))
        
    def get_rate_value(self):
        return self.speech_rate_slider.value()
    
    def get_volume_value(self):
        return self.speech_volume_slider.value() / 100.0
    
    def tabHandler(self, arrow=None):
        print("tab")
        if(arrow == "down"):
            self.currentfocus -= 1
            if(self.currentfocus < 0):
                self.currentfocus = len(self.setting_layout) - 1
        else:
            self.currentfocus += 1
            if(self.currentfocus > len(self.setting_layout) - 1):
                self.currentfocus = 0
            self.setting_layout[self.currentfocus].setFocus()
        intro = self.setting_layout[self.currentfocus].accessibleDescription()
        speak(intro)

class RightWidget(QWidget):
    """
    This class respresent the right widget.\n
    It contains command panel , query place.
    """

    def __init__(self):
        super().__init__()
        global internal_speak_engine

        self.chatbot_button = QPushButton("Chat Bot")
        self.chatbot_button.setAccessibleDescription("A chat bot that answer your questions.")

        #login components
        self.loginButton = QPushButton("Login")
        self.loginButton.setAccessibleDescription("Login your Chess.com account for more functions")

        self.loginAccount_Input = QLineEdit()
        self.loginAccount_Input.setPlaceholderText("Username or Email")
        self.loginAccount_Input.setAccessibleDescription("The place to type in Username or Email")

        self.loginPassword_Input = QLineEdit()
        self.loginPassword_Input.setPlaceholderText("Password")
        self.loginPassword_Input.setAccessibleDescription("The place to type in Password")
        self.loginPassword_Input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_button = QPushButton("Login")
        self.login_button.setAccessibleDescription("Press to login")
        self.login_button.setAutoDefault(True)

        self.settingButton = QPushButton("Setting")
        self.settingButton.setAccessibleDescription("Menu to change your preferences")

        #Computer mode components
        self.playWithComputerButton = QPushButton("Play with computer")
        self.playWithComputerButton.setText("Play with computer")
        self.playWithComputerButton.setAccessibleName("Play with computer")
        self.playWithComputerButton.setAccessibleDescription(
            "press space or enter to play with computer engine"
        )

        # self.playWithComputerButton_BackToSchoolButton = QPushButton("Back To School")
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

        self.combobox_coach = QComboBox()
        self.combobox_coach.setAccessibleDescription("Coach Combobox")
        self.combobox_adaptive = QComboBox()
        self.combobox_adaptive.setAccessibleDescription("Adaptive Combobox")
        self.combobox_beginner = QComboBox()
        self.combobox_beginner.setAccessibleDescription("Beginner Combobox")
        self.combobox_intermediate = QComboBox()
        self.combobox_intermediate.setAccessibleDescription("Intermediate Combobox")
        self.combobox_advanced = QComboBox()
        self.combobox_advanced.setAccessibleDescription("Advanced Combobox")
        self.combobox_master = QComboBox()
        self.combobox_master.setAccessibleDescription("Master Combobox")
        self.combobox_athletes = QComboBox()
        self.combobox_athletes.setAccessibleDescription("Athletes Combobox")
        self.combobox_musicians = QComboBox()
        self.combobox_musicians.setAccessibleDescription("Musicians Combobox")
        self.combobox_creators = QComboBox()
        self.combobox_creators.setAccessibleDescription("Creators Combobox")
        self.combobox_top_players = QComboBox()
        self.combobox_top_players.setAccessibleDescription("Top Players Combobox")
        self.combobox_personalities = QComboBox()
        self.combobox_personalities.setAccessibleDescription("Personalities Combobox")
        self.combobox_engine = QComboBox()
        self.combobox_engine.setAccessibleDescription("Engine Combobox")

        self.play_button = QPushButton("Play")
        self.play_button.setAutoDefault(True)

        self.back_to_category_button = QPushButton("Back to Category")
        self.back_to_category_button.setAutoDefault(True)

        for item in coach:
            self.combobox_coach.addItem(item.value["name"])
            self.combobox_coach.setItemData(self.combobox_coach.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in adaptive:
            self.combobox_adaptive.addItem(item.value["name"])
            self.combobox_adaptive.setItemData(self.combobox_adaptive.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in beginner:
            self.combobox_beginner.addItem(item.value["name"])
            self.combobox_beginner.setItemData(self.combobox_beginner.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in intermediate:
            self.combobox_intermediate.addItem(item.value["name"])
            self.combobox_intermediate.setItemData(self.combobox_intermediate.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in advanced:
            self.combobox_advanced.addItem(item.value["name"])
            self.combobox_advanced.setItemData(self.combobox_advanced.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in master:
            self.combobox_master.addItem(item.value["name"])
            self.combobox_master.setItemData(self.combobox_master.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in athletes:
            self.combobox_athletes.addItem(item.value["name"])
            self.combobox_athletes.setItemData(self.combobox_athletes.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in musicians:
            self.combobox_musicians.addItem(item.value["name"])
            self.combobox_musicians.setItemData(self.combobox_musicians.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in creators:
            self.combobox_creators.addItem(item.value["name"])
            self.combobox_creators.setItemData(self.combobox_creators.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in top_players:
            self.combobox_top_players.addItem(item.value["name"])
            self.combobox_top_players.setItemData(self.combobox_top_players.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
        for item in personalities:
            self.combobox_personalities.addItem(item.value["name"])
            self.combobox_personalities.setItemData(self.combobox_personalities.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                            Qt.ItemDataRole.AccessibleTextRole)
            
        for item in engine:
            self.combobox_engine.addItem(item.value["name"])
            self.combobox_engine.setItemData(self.combobox_engine.count() - 1,
                                            f"{item.value['name']}\n Rating: {item.value['rating']}",
                                                Qt.ItemDataRole.AccessibleTextRole)

        #Online mode components
        self.playWithOtherButton = QPushButton("Play with other online player")
        self.playWithOtherButton.setAccessibleName("Play with other online player")
        self.playWithOtherButton.setAccessibleDescription(
            "press space or enter to play with other online player"
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

        #Puzzle mode components
        self.puzzleModeButton = QPushButton("Puzzle Mode")
        self.puzzleModeButton.setAccessibleDescription("press space or enter to play chess puzzle")
        self.nextPuzzleButton = QPushButton("Next Puzzle")
        self.retryPuzzleButton = QPushButton("Retry Puzzle")

        #Game end components
        self.newgameButton = QPushButton("New Game")
        self.gamereviewButton = QPushButton("Game Review")
        self.returnToHomePageButton = QPushButton("Return to Home Page")
        self.returnToHomePageButton.setAccessibleDescription("Press to exit current mode")
        self.returnToHomePageButton.setAutoDefault(True)

        #Analysis mode components
        self.analysisCurrentMove = QLabel()
        self.analysisCurrentMove.setText("Current Move: \n")
        self.analysisCurrentMove.setWordWrap(True)

        self.analysisComment = QLabel()
        self.analysisComment.setText("Game Review Comment: \n")
        self.analysisComment.setWordWrap(True)

        self.analysisExplanation = QLabel()
        self.analysisExplanation.setText("Explanation: \n")
        self.analysisExplanation.setWordWrap(True)

        self.analysis_NextMove_Button = QPushButton("Next Move")
        self.analysis_PreviousMove_Button = QPushButton("Previous Move")
        self.analysis_FirstMove_Button = QPushButton("First Move")
        # self.analysis_Explanation_Button = QPushButton("Explanation")
        self.analysis_BestMove_Button = QPushButton("Best Move")
        # self.analysis_CurrentMove_Button = QPushButton("Current Move")        
        # self.analysis_LastMove_Button = QPushButton("Last Move")

        self.moveList = QLabel()
        self.moveList.setText("Move List:\n")

        self.whitePieces = QLabel()
        self.whitePieces.setText("White pieces: ")

        self.blackPieces = QLabel()
        self.blackPieces.setText("Black pieces: ")

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

        self.check_being_attacked = QPushButton("Macro View")
        self.check_being_attacked.setAutoDefault(True)

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

        smallfont = QFont()
        smallfont.setPointSize(7)
        self.moveList.setFont(smallfont)

        self.login_menu = []
        self.login_menu.append(self.loginAccount_Input)
        self.login_menu.append(self.loginPassword_Input)
        self.login_menu.append(self.login_button)

        self.setting_menu = []
        self.setting_menu.append(self.loginButton)
        self.setting_menu.append(self.playWithComputerButton)
        self.setting_menu.append(self.playWithOtherButton)
        self.setting_menu.append(self.puzzleModeButton)
        self.setting_menu.append(self.chatbot_button)

        self.play_menu = []
        self.play_menu.append(self.whitePieces)
        self.play_menu.append(self.blackPieces)
        self.play_menu.append(self.colorBox)
        self.play_menu.append(self.moveList)
        self.play_menu.append(self.opponentBox)
        self.play_menu.append(self.resign)
        self.play_menu.append(self.check_time)
        self.play_menu.append(self.check_being_attacked)
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

        self.bot_category_select_menu = []
        self.bot_category_select_menu.append(self.playWithComputerButton_Coach)
        self.bot_category_select_menu.append(self.playWithComputerButton_Adaptive)
        self.bot_category_select_menu.append(self.playWithComputerButton_Beginner)
        self.bot_category_select_menu.append(self.playWithComputerButton_Intermediate)
        self.bot_category_select_menu.append(self.playWithComputerButton_Advanced)
        self.bot_category_select_menu.append(self.playWithComputerButton_Master)
        self.bot_category_select_menu.append(self.playWithComputerButton_Athletes)
        self.bot_category_select_menu.append(self.playWithComputerButton_Musicians)
        self.bot_category_select_menu.append(self.playWithComputerButton_Creators)
        self.bot_category_select_menu.append(self.playWithComputerButton_TopPlayers)
        self.bot_category_select_menu.append(self.playWithComputerButton_Personalities)
        self.bot_category_select_menu.append(self.playWithComputerButton_Engine)

        self.bot_combobox = []
        self.bot_combobox.append(self.combobox_coach)
        self.bot_combobox.append(self.combobox_adaptive)
        self.bot_combobox.append(self.combobox_beginner)
        self.bot_combobox.append(self.combobox_intermediate)
        self.bot_combobox.append(self.combobox_advanced)
        self.bot_combobox.append(self.combobox_master)
        self.bot_combobox.append(self.combobox_athletes)
        self.bot_combobox.append(self.combobox_musicians)
        self.bot_combobox.append(self.combobox_creators)
        self.bot_combobox.append(self.combobox_top_players)
        self.bot_combobox.append(self.combobox_personalities)
        self.bot_combobox.append(self.combobox_engine)

        self.game_end_menu = []
        self.game_end_menu.append(self.newgameButton)
        self.game_end_menu.append(self.gamereviewButton)

        self.puzzle_end_menu = []
        self.puzzle_end_menu.append(self.nextPuzzleButton)
        self.puzzle_end_menu.append(self.retryPuzzleButton)

        self.analysis_menu = []
        self.analysis_menu.append(self.analysisCurrentMove)
        self.analysis_menu.append(self.analysisComment)
        self.analysis_menu.append(self.analysisExplanation)
        self.analysis_menu.append(self.analysis_PreviousMove_Button)
        self.analysis_menu.append(self.analysis_NextMove_Button)
        self.analysis_menu.append(self.analysis_FirstMove_Button)
        # self.analysis_menu.append(self.analysis_LastMove_Button)
        # self.analysis_menu.append(self.analysis_Explanation_Button)
        self.analysis_menu.append(self.analysis_BestMove_Button)
        # self.analysis_menu.append(self.analysis_CurrentMove_Button)

        #analysis control button
        self.analysisButton = []
        self.analysisButton.append(self.analysis_PreviousMove_Button)
        self.analysisButton.append(self.analysis_NextMove_Button)
        self.analysisButton.append(self.analysis_FirstMove_Button)
        # self.analysisButton.append(self.analysis_LastMove_Button)
        # self.analysisButton.append(self.analysis_Explanation_Button)
        self.analysisButton.append(self.analysis_BestMove_Button)
        # self.analysisButton.append(self.analysis_CurrentMove_Button)

        self.setting_layout = QVBoxLayout()

        for item in self.analysisButton:
            item.setAutoDefault(True)
            
        for item in self.setting_menu:
            self.setting_layout.addWidget(item)
            item.setAutoDefault(True)

        for item in self.login_menu:
            self.setting_layout.addWidget(item)
            item.hide()

        self.login_menu.append(self.returnToHomePageButton)

        for item in self.play_menu:
            self.setting_layout.addWidget(item)
            item.hide()

        for item in self.online_mode_select_menu:
            self.setting_layout.addWidget(item)
            item.setAutoDefault(True)
            item.hide()
        
        self.online_mode_select_menu.append(self.returnToHomePageButton)

        for item in self.bot_category_select_menu:
            self.setting_layout.addWidget(item)
            item.setAutoDefault(True)
            item.hide()

        self.bot_category_select_menu.append(self.returnToHomePageButton)        

        for item in self.bot_combobox:
            self.setting_layout.addWidget(item)
            item.hide()

        self.setting_layout.addWidget(self.play_button)
        self.play_button.hide()
        self.setting_layout.addWidget(self.back_to_category_button)
        self.back_to_category_button.hide()

        for item in self.game_end_menu:
            self.setting_layout.addWidget(item)
            item.setAutoDefault(True)
            item.hide()

        self.game_end_menu.append(self.returnToHomePageButton)

        for item in self.puzzle_end_menu:
            self.setting_layout.addWidget(item)
            item.setAutoDefault(True)
            item.hide()

        self.puzzle_end_menu.append(self.returnToHomePageButton)

        for item in self.analysis_menu:
            self.setting_layout.addWidget(item)
            item.hide()

        self.analysis_menu.append(self.returnToHomePageButton)

        self.setting_layout.addWidget(self.returnToHomePageButton)
        self.returnToHomePageButton.hide()

        self.setting_layout.addWidget(self.settingButton) #setting button
        self.setting_menu.append(self.settingButton)
        self.online_mode_select_menu.append(self.settingButton)
        self.play_menu.append(self.settingButton)
        self.analysis_menu.append(self.settingButton)
        
        self.settingButton.setAutoDefault(True)
        self.settingButton.show()

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

    keyPressed_Signal = pyqtSignal(int)

    def show_information_box(self):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Information")
        message_box.setText("This is an information message.")
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.setFocus()
        message_box.exec()

    # check whether user logined
    def checkLogined(self):
        def callback(x):
            self.userLoginName = x
            print(f"Login User: {self.userLoginName}")
            if(self.userLoginName != None):
                self.rightWidget.setting_layout.removeWidget(self.rightWidget.loginButton)
                self.rightWidget.setting_menu.remove(self.rightWidget.loginButton)
                self.rightWidget.loginButton.hide()
            self.currentFocus = len(self.rightWidget.setting_menu) - 1
            self.rightWidget.loginButton.setFocus()

        jsCode = """
            function checkLogin() {{
                return document.querySelector(".home-user-info")?.outerText
            }}
            checkLogin();
            """
        self.leftWidget.chessWebView.page().runJavaScript(jsCode, callback)

    # User Login
    def loginHandler(self):
        def checkLogin(success):
            if(success):
                self.userLoginName = username
                self.rightWidget.setting_layout.removeWidget(self.rightWidget.loginButton)
                self.rightWidget.setting_menu.remove(self.rightWidget.loginButton)
                self.change_main_flow_status(Bot_flow_status.setting_status)
                print(f"login success! Username: {self.userLoginName}")
                speak(f"login success! Username: {self.userLoginName}")
            else:
                print("The username or password is incorrect. Please try again")
                speak("The username or password is incorrect. Please try again")

        username = self.rightWidget.loginAccount_Input.text()
        password = self.rightWidget.loginPassword_Input.text()
        print(f"username: {username}")
        print(f"password: {password}")
        self.rightWidget.loginAccount_Input.clear()
        self.rightWidget.loginPassword_Input.clear()
        if(username == "" or password == ""):
            print("Invalid Input")
            speak("Invalid Input")
            return
        self.leftWidget.chessWebView.page().runJavaScript(js_function.userLogin + f"userLogin('{username}', '{password}')")
        speak("trying to login")
        QTimer.singleShot(3000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.loginSuccess, checkLogin))

    ##change the application flow status and re-init / clean the variable
    def change_main_flow_status(self, status):
        print("change status", status)
        match status:
            case Bot_flow_status.login_status:
                speak("Activate Login Phase")
                self.leftWidget.chessWebView.load(QUrl("https://www.chess.com/login"))
                self.main_flow_status = Bot_flow_status.login_status
                self.currentFocus = len(self.rightWidget.login_menu) - 1
                for item in self.rightWidget.setting_menu:
                    item.hide()
                for item in self.rightWidget.login_menu:
                    item.show()
                self.rightWidget.loginAccount_Input.setFocus()

            case Bot_flow_status.setting_status:
                self.getOpponentMoveTimer.stop()
                self.check_game_end_timer.stop()
                self.getScoreTimer.stop()
                self.main_flow_status = Bot_flow_status.setting_status
                self.game_play_mode = None
                self.input_mode = Input_mode.command_mode
                self.rightWidget.commandPanel.setAccessibleDescription(
                    "type the letter 'C' for computer mode, type the letter 'O' for online players mode "
                )
                self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H"]
                self.number = ["1", "2", "3", "4", "5", "6", "7", "8"]
                self.moveList_line = 1
                self.moveList_element = 0
                self.moveListString = ""
                self.chessBoard = None
                self.change_game_mode(None)
                self.rightWidget.colorBox.setText("Assigned Color: ")
                self.userColor = None
                self.opponentColor = None
                self.category_combobox = None
                self.bot_retry = False
                self.rightWidget.right_layout = self.rightWidget.setting_layout
                self.rightWidget.opponentBox.setText("Opponent move: \n")
                try:
                    for i in range(8):
                        for j in range(8):
                            if(isinstance(self.leftWidget.grids[i][j], QLabel)):
                                self.leftWidget.grids[i][j].deleteLater()
                except:
                    print("No grids need to delete")
                for item in range(self.rightWidget.setting_layout.count()):
                    self.rightWidget.setting_layout.itemAt(item).widget().hide()
                for item in self.rightWidget.setting_menu:
                    item.show() 
                self.currentFocus = len(self.rightWidget.setting_menu) - 1
                return
                
            case Bot_flow_status.select_status:
                self.main_flow_status = Bot_flow_status.select_status
                self.game_flow_status = Game_flow_status.not_start
                for item in self.rightWidget.setting_menu:
                    item.hide()
                match self.game_play_mode:
                    case Game_play_mode.computer_mode:
                        self.currentFocus = len(self.rightWidget.bot_category_select_menu)
                        for item in self.rightWidget.bot_category_select_menu:
                            item.show()
                        self.leftWidget.chessWebView.page().runJavaScript(js_function.open_bot_menu)
                        speak("Select bot category")
                    case Game_play_mode.online_mode:
                        self.currentFocus = len(self.rightWidget.online_mode_select_menu) - 1
                        for item in self.rightWidget.online_mode_select_menu:
                            item.show()
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
                for item in range(self.rightWidget.setting_layout.count()):
                    self.rightWidget.setting_layout.itemAt(item).widget().hide()
                for item in self.rightWidget.play_menu:
                    item.show()
                self.chessBoard = None
                self.userColor = None
                self.opponentColor = None
                # self.leftWidget.grids = dict()
                return
            
            case Bot_flow_status.game_play_status:
                self.check_game_end_timer.start(2000)
                self.rightWidget.commandPanel.setFocus()
                self.currentFocus = len(self.rightWidget.play_menu) - 1
                self.main_flow_status = Bot_flow_status.game_play_status
                return
            
            case Bot_flow_status.game_end_status:
                self.moveList_line = 1
                self.moveList_element = 0
                self.arrow_mode_switch(False)
                self.input_mode = Input_mode.command_mode
                self.getOpponentMoveTimer.stop()
                self.check_game_end_timer.stop()
                self.getScoreTimer.stop()
                self.rightWidget.whitePieces.setText("White pieces: ")
                self.rightWidget.blackPieces.setText("Black pieces: ")
                self.input_mode = Input_mode.command_mode
                self.chessBoard = None
                for item in range(self.rightWidget.setting_layout.count()):
                    self.rightWidget.setting_layout.itemAt(item).widget().hide()
                for item in self.rightWidget.game_end_menu:
                    item.show()
                self.currentFocus = len(self.rightWidget.game_end_menu) - 1
                self.main_flow_status = Bot_flow_status.game_end_status

            case Bot_flow_status.puzzle_end_status:
                self.arrow_mode_switch(False)
                self.input_mode = Input_mode.command_mode
                self.main_flow_status = Bot_flow_status.puzzle_end_status
                for item in range(self.rightWidget.setting_layout.count()):
                    self.rightWidget.setting_layout.itemAt(item).widget().hide()
                for item in self.rightWidget.puzzle_end_menu:
                    item.show()
                self.currentFocus = len(self.rightWidget.puzzle_end_menu)

    ##change the application game mode
    def change_game_mode(self, mode):
        match mode:
            case None:
                self.game_play_mode = None
            case Game_play_mode.analysis_mode:
                self.currentFocus = len(self.rightWidget.analysis_menu) - 1
                self.game_play_mode = Game_play_mode.analysis_mode
                for item in range(self.rightWidget.setting_layout.count()):
                    self.rightWidget.setting_layout.itemAt(item).widget().hide()
                for item in self.rightWidget.analysis_menu:
                    item.show()

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
        self.game_play_mode = Game_play_mode.computer_mode
        speak(
            "computer engine mode <>" + Speak_template.initialize_game_sentense.value,
            True,
        )
        self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(4000, self.checkExistGame))

        self.leftWidget.chessWebView.load(
            QUrl("https://www.chess.com/play/computer")
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
        self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(3000, self.checkExistGame))
        self.leftWidget.chessWebView.load(QUrl("https://www.chess.com/play/online"))

    def selectPanelHandler(self):
        input = self.rightWidget.selectPanel.text().lower()
        if(self.game_play_mode == Game_play_mode.computer_mode):
            print("no idea")
        elif(self.game_play_mode == Game_play_mode.online_mode):
            for selection in timeControlDeterminant_Type:
                if input in selection.value:
                    self.online_select_timeControl(selection.value[input])
    
    # handle select timecontrol
    def online_select_timeControl(self, timeControl, skip=False):
        def clickNCapture(x):
            def test(clocks):
                if clocks == None or clocks[0] == clocks[1]:
                        self.leftWidget.checkTime(test)
                else:
                    print("clocks detected :", clocks)
                    QTimer.singleShot(2000, board)
                    
            self.leftWidget.checkTime(test)
        
        def board():
            self.getColor()
            self.initBoard()
            self.getBoard()

        print(f"timeControl = {timeControl}")
        self.timeControl = timeControl

        if(skip):
            self.leftWidget.chessWebView.loadFinished.disconnect()
        
        for item in self.rightWidget.online_mode_select_menu:
            item.hide()

        for item in self.rightWidget.play_menu:
            item.show()
        if self.userLoginName != None:
            print("login name", self.userLoginName)
            self.leftWidget.chessWebView.page().runJavaScript(js_function.clickTimeControlButton + f"clickTimeControlButton('{timeControl}', true)", clickNCapture)
        else:
            print("No login")
            self.leftWidget.chessWebView.page().runJavaScript(js_function.clickTimeControlButton + f"clickTimeControlButton('{timeControl}', false)", clickNCapture)

    #handle select bot
    def select_bot(self):
        def callback1(x):
            print("select bot")
            if(self.bot_retry):
                QTimer.singleShot(1000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.select_bot + f"select_bot('{self.category_combobox.currentText()}');"))
                QTimer.singleShot(2000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.check_bot_locked, callback2))
                return
            QTimer.singleShot(1000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.check_bot_locked, callback2))

        def callback2(locked):
            print(f"locked = {locked}")
            if(locked):
                # self.leftWidget.chessWebView.load(
                #     QUrl("https://www.chess.com/play/computer")
                # )
                speak("The bot is locked for guest or non-premium account. Please select another bot.")
                self.bot_retry = True
            else:
                self.category_combobox.hide()
                self.rightWidget.play_button.hide()
                self.rightWidget.back_to_category_button.hide()
                for item in self.rightWidget.play_menu:
                    item.show()
                board()
                speak("Bot game Started")

        def board():
            self.getColor()
            self.initBoard()
            self.getBoard()

        print(f"Bot: {self.category_combobox.currentText()}")
        if(self.category_combobox == self.rightWidget.combobox_engine):
            level = self.category_combobox.currentText().split()[1]
            print(level)
            self.leftWidget.chessWebView.page().runJavaScript(js_function.select_engine_level + f"select_engine_level('{level}');", callback1)
            return
        
        self.leftWidget.chessWebView.page().runJavaScript(js_function.select_bot + f"select_bot('{self.category_combobox.currentText()}');", callback1)

    #handle select bot category
    def bot_select_category(self, category):
        for item in self.rightWidget.bot_category_select_menu:
            item.hide()
        match category:
            case "coach":
                self.category_combobox = self.rightWidget.combobox_coach
            case "adaptive":
                self.category_combobox = self.rightWidget.combobox_adaptive
            case "beginner":
                self.category_combobox = self.rightWidget.combobox_beginner
            case "intermediate":
                self.category_combobox = self.rightWidget.combobox_intermediate
            case "advanced":
                self.category_combobox = self.rightWidget.combobox_advanced
            case "master":
                self.category_combobox = self.rightWidget.combobox_master
            case "athletes":
                self.category_combobox = self.rightWidget.combobox_athletes
            case "musicians":
                self.category_combobox = self.rightWidget.combobox_musicians
            case "creators":
                self.category_combobox = self.rightWidget.combobox_creators
            case "top_players":
                self.category_combobox = self.rightWidget.combobox_top_players
            case "personalities":
                self.category_combobox = self.rightWidget.combobox_personalities
            case "engine":
                self.category_combobox = self.rightWidget.combobox_engine
        self.category_combobox.show()
        self.rightWidget.play_button.show()
        self.rightWidget.back_to_category_button.show()
        self.currentFocus = 3
        speak("Please first select the bot you want to play, then click play to start")

    #function for return to category selection
    def back_to_category(self):
        print("Return to Category")
        self.category_combobox.hide()
        self.rightWidget.play_button.hide()
        self.rightWidget.back_to_category_button.hide()
        for item in self.rightWidget.bot_category_select_menu:
            item.show()
        self.category_combobox = None
        self.currentFocus = len(self.rightWidget.bot_category_select_menu)

    #function to speak out selected bot
    def bot_information(self, index, select=False):
        print(index)
        if(select):
            print(index)
            print(f"{self.category_combobox.currentText()} is selected")
            speak(f"{self.category_combobox.currentText()} is selected")
            return
        # index = self.category_combobox.currentIndex()
        intro = self.category_combobox.itemData(index, Qt.ItemDataRole.AccessibleTextRole)
        speak(intro)

    #function to check whether unfinished game exist
    def checkExistGame(self):
        def callback(moveList):
            print(f"movemovmeomvomeovmo = {moveList}")
            if(moveList):
                self.change_main_flow_status(Bot_flow_status.board_init_status)
                self.getColor(exist_game="Existing Game Founded. ")
                self.initBoard()
                print("reconstructing the board")
                self.getBoard()

                for move in moveList:
                    print(self.moveList_element)
                    if(self.moveList_element % 10 == 0 and self.moveList_element != 0):
                        self.moveListString += "\n"
                    if (self.moveList_element % 2 == 0):
                        self.moveListString += str(self.moveList_line) + ". " + self.chessBoard.board_object.parse_san(move).uci() + ", "
                    else:
                        self.moveListString += self.chessBoard.board_object.parse_san(move).uci() + ", "
                        self.moveList_line += 1
                    self.moveList_element += 1
                    if(self.moveList_element == len(moveList)):
                        self.rightWidget.opponentBox.setText(f"opponent last move: {self.chessBoard.board_object.parse_san(move).uci()}")
                    self.chessBoard.board_object.push_san(move)
                self.rightWidget.moveList.setText("Move List:\n" + self.moveListString)
        
                print(self.chessBoard.board_object)
                self.previous_game_exist = True
                turn = "WHITE" if(self.moveList_element %2==0) else "BLACK"
                print(f"current turn: {turn}")
                self.game_flow_status = Game_flow_status.user_turn if(turn==self.userColor) else Game_flow_status.opponent_turn
                print("Existing Game Founded")
                self.change_main_flow_status(Bot_flow_status.game_play_status)      
                return

            else:
                print("no existing board")
                self.change_main_flow_status(Bot_flow_status.select_status)


        self.leftWidget.chessWebView.loadFinished.disconnect()
        self.leftWidget.chessWebView.page().runJavaScript(js_function.checkExistGame, callback)

    def getPiecesLocation(self, location):
        self.rightWidget.whitePieces.setText(f"White pieces: " + location[0])
        self.rightWidget.blackPieces.setText(f"Black pieces: " + location[1])


## Puzzle Mode Start:

    def puzzleModeHandler(self):
        if(self.game_flow_status == Bot_flow_status.game_play_status):
            return
        speak(Speak_template.initialize_game_sentense.value, True)
        self.main_flow_status = self.change_main_flow_status(Bot_flow_status.board_init_status)
        self.leftWidget.chessWebView.load(QUrl("https://www.chess.com/puzzles/rated"))
        self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(4000, self.puzzle_mode_InitBoard))

    def puzzle_mode_InitBoard(self):
        try:
            self.leftWidget.chessWebView.loadFinished.disconnect()
        except:
            print("no load finish connected")
        self.getOpponentMoveTimer.stop()
        self.rightWidget.resign.hide()
        self.rightWidget.check_time.hide()
        self.rightWidget.moveList.hide()
        self.count = 0
        self.puzzle_mode_GetTitle()

    def puzzle_mode_GetTitle(self):
        def callback(title):
            if(self.userColor == None):
                match title:
                    case "White":
                        self.row, self.col = 0, 0
                        self.userColor = title.upper()
                        self.opponentColor = "BLACK"
                        self.currentPos = 'a1'
                        print(f"User: {self.userColor}, Oppoenent: {self.opponentColor}")
                    case "Black":
                        self.row, self.col = 7, 7
                        self.userColor = title.upper()
                        speak("You are playing as black.")
                        self.opponentColor = "WHITE"
                        self.currentPos = 'h8'
                        print(f"User: {self.userColor}, Oppoenent: {self.opponentColor}")
                
                try:
                    self.rightWidget.colorBox.setText("Assigned Color: " + self.userColor)
                    self.puzzle_mode_ConstructBoard()
                except:
                    speak("You have reach the puzzle limit for your account. Returning to home page.")
                    self.leftWidget.chessWebView.load(QUrl("https://www.chess.com"))
                    self.change_main_flow_status(Bot_flow_status.setting_status)
            else:
                match title:
                    case "Correct" | "Solved":
                        print("Correct")
                        speak("Correct. Please select next action.")
                        self.game_flow_status = self.change_main_flow_status(Bot_flow_status.puzzle_end_status)
                    #button click next
                    case "Incorrect":
                        print("Incorrect, puzzle run ended")
                        speak("Incorrect, puzzle run ended")
                        self.change_main_flow_status(Bot_flow_status.puzzle_end_status)
                    case _:
                        # self.puzzle_getOppMove_sgn.emit()
                        self.puzzle_mode_GetMove()

        self.leftWidget.chessWebView.page().runJavaScript(js_function.puzzle_mode_GetTitle, callback)

    def puzzle_mode_ConstructBoard(self):
        def callback(board):
            self.FenNotation = ""
            self.boardDescription = []
            self.whiteLoc = []
            self.blackLoc = []
            for row in reversed(range(8)):
                count = 0
                for column in range(8):
                    if(board[row][column]!=0):
                        alphabet_column = list(CHESSBOARD_LOCATION_CONVERSION.keys())[list(CHESSBOARD_LOCATION_CONVERSION.values()).index(str(column+1))]  #find the alphabet form column
                        piece_loc = PIECES_SHORTFORM_CONVERTER[board[row][column]] + ": " + alphabet_column + str(row+1)
                        if(board[row][column] in ['Q', 'N', 'R', 'B', 'P', 'K']):
                            self.whiteLoc.append(piece_loc)
                        else:
                            self.blackLoc.append(piece_loc)
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
            print(self.whiteLoc)
            print(self.blackLoc)
            self.rightWidget.commandPanel.setFocus()
            self.currentFocus = len(self.rightWidget.play_menu) - 1
            self.main_flow_status = Bot_flow_status.game_play_status
            self.game_play_mode = Game_play_mode.puzzle_mode
            self.chessBoard = ChessBoard(self.FenNotation)
            self.game_flow_status = Game_flow_status.opponent_turn
            self.puzzle_mode_GetTitle()

        self.initBoard()
        self.leftWidget.chessWebView.page().runJavaScript(js_function.puzzle_mode_constructBoard, callback)

    def puzzle_mode_GetMove(self):
        def callback(uci_move):
            print(uci_move)
            pos1 = uci_move[0] + uci_move[1]
            pos2 = uci_move[2] + uci_move[3]
            pos1_piece = self.chessBoard.check_grid(pos1)
            print(f'pos1_piece = {pos1_piece}')
            print(f"count = {self.count}")
            if(self.count == 0):
                if(pos1_piece == None):
                    dest = pos2
                    src = pos1
                else:
                    dest = pos1
                    src = pos2
            else:
                if(pos1_piece == None):
                    dest = pos1
                    src = pos2
                else:
                    dest = pos2
                    src = pos1
            if(self.game_flow_status == Game_flow_status.opponent_turn):
                print(f"Opponent Last Move: {src} to {dest}")
                speak(f"Opponent Last Move: {src} to {dest}")
                if(self.count != 0):
                    self.chessBoard.moveWithValidate(src + dest)
                    print(self.chessBoard.board_object)
                self.count += 1
                self.rightWidget.opponentBox.setText(f"Opponent Last Move: {src} to {dest}")
                if(self.count == 1):
                    if self.userColor == "WHITE":
                        speak("You are playing as white\n" + self.rightWidget.whitePieces.text() + self.rightWidget.blackPieces.text() + self.rightWidget.opponentBox.text())
                    else:
                        speak("You are playing as black\n" + self.rightWidget.whitePieces.text() + self.rightWidget.blackPieces.text() + self.rightWidget.opponentBox.text())
                self.game_flow_status = Game_flow_status.user_turn
            else:
                print("no update move")
                return
            
            self.leftWidget.chessWebView.page().runJavaScript(js_function.getPiecesLocation, self.getPiecesLocation)

        if self.input_mode == Input_mode.arrow_mode:
            self.all_grids_switch(True)
        self.leftWidget.chessWebView.page().runJavaScript(js_function.puzzle_mode_GetOpponentMove, callback)

    def puzzle_movePiece(self, move):
        movePair = self.chessBoard.moveWithValidate(move)
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

            target_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[0].lower()]) - 1 
            target_row = int(uci_string[1]) - 1
            dest_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[2].lower()]) - 1   #index
            dest_row = int(uci_string[3]) - 1
            dest = uci_string[2:4]
            print(f"dest_row: {dest_row}, dest_col: {dest_col}")
            promoteTo = uci_string[4].lower()
            promote_index = list(PIECE_TYPE_CONVERSION).index(promoteTo)

            print(f"promote_index: {promote_index}")

            # dlg = confirmMoveDialog("pawn", dest, promote=promoteTo)
            dlg = confirmDialog(human_string)
            if dlg.exec():
                self.all_grids_switch(False)
                targetWidget = self.leftWidget.grids[target_col][target_row]
                destWidget = self.leftWidget.grids[dest_col][dest_row]
                if widgetDragDrop(targetWidget, destWidget):
                    match self.userColor:
                        case "BLACK":
                            promoteRow = dest_row + promote_index
                        case "WHITE":
                            promoteRow =  dest_row - promote_index
                    print(f"dest_col: {dest_col}, promoteRow: {promoteRow}")
                    promoteWidget = self.leftWidget.grids[dest_col][promoteRow]
                    if widgetClick(promoteWidget):
                        self.rightWidget.commandPanel.clear()
                        self.game_flow_status = Game_flow_status.opponent_turn
                        QTimer.singleShot(500, self.focus_back)
            else:
                self.chessBoard.board_object.pop()
                self.rightWidget.commandPanel.clear()
                print("Cancel!")

        elif len(uci_string) == 4:

            target_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[0].lower()]) - 1
            target_row = int(uci_string[1]) - 1
            dest_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[2].lower()]) - 1
            dest_row = int(uci_string[3]) - 1
            dest = uci_string[2:4]
            # dlg = confirmMoveDialog(target_type, dest)
            dlg = confirmDialog(human_string)
            if dlg.exec():
                self.all_grids_switch(False)
                # QTimer.singleShot(3000, partial(self.clickStart,input))
                # print(self.chessBoard.board_object)

                targetWidget = self.leftWidget.grids[target_col][target_row]
                destWidget = self.leftWidget.grids[dest_col][dest_row]
                self.rightWidget.commandPanel.clear()
                if widgetDragDrop(targetWidget, destWidget):
                    self.game_flow_status = Game_flow_status.opponent_turn
                    QTimer.singleShot(500, self.focus_back)
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
            speak(move + movePair)
            print(move + movePair)  ##error move speak
            self.rightWidget.commandPanel.clear()
        
        QTimer.singleShot(1000, self.puzzle_mode_GetTitle)
        QTimer.singleShot(500, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.getPiecesLocation, self.getPiecesLocation))

    def clickNextPuzzle(self):
        def callback(x):
            self.userColor = None
            self.change_main_flow_status(Bot_flow_status.board_init_status)
            QTimer.singleShot(2000, self.puzzle_mode_InitBoard)

        self.leftWidget.chessWebView.page().runJavaScript(js_function.clickNextPuzzle, callback)

    def retryPuzzle(self):
        def callback(x):
            self.userColor = None
            self.change_main_flow_status(Bot_flow_status.board_init_status)
            QTimer.singleShot(2000, self.puzzle_mode_InitBoard)

        self.leftWidget.chessWebView.page().runJavaScript(js_function.retryPuzzle, callback)

## Puzzle Mode End

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
            self.change_main_flow_status(Bot_flow_status.game_end_status)
            def callBack():
                self.game_flow_status = Game_flow_status.game_end
                speak(Speak_template.user_resign.value)
                self.getOpponentMoveTimer.stop()
                self.getScoreTimer.start(1000)
                return

            if (
                self.userLoginName == None
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

    #focus on grid or keyboard-based interface
    def focus_back(self):
            if self.input_mode == Input_mode.arrow_mode:
                self.leftWidget.grids[self.col][self.row].setFocus()
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

            target_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[0].lower()]) - 1 
            target_row = int(uci_string[1]) - 1
            dest_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[2].lower()]) - 1   #index
            dest_row = int(uci_string[3]) - 1
            dest = uci_string[2:4]
            print(f"dest_row: {dest_row}, dest_col: {dest_col}")
            promoteTo = uci_string[4].lower()
            promote_index = list(PIECE_TYPE_CONVERSION).index(promoteTo)

            print(f"promote_index: {promote_index}")

            # dlg = confirmMoveDialog("pawn", dest, promote=promoteTo)
            dlg = confirmDialog(human_string)
            if dlg.exec():
                self.all_grids_switch(False)
                targetWidget = self.leftWidget.grids[target_col][target_row]
                destWidget = self.leftWidget.grids[dest_col][dest_row]
                if widgetDragDrop(targetWidget, destWidget):
                    match self.userColor:
                        case "BLACK":
                            promoteRow = dest_row + promote_index
                        case "WHITE":
                            promoteRow =  dest_row - promote_index
                    print(f"dest_col: {dest_col}, promoteRow: {promoteRow}")
                    promoteWidget = self.leftWidget.grids[dest_col][promoteRow]
                    if widgetClick(promoteWidget):
                        self.rightWidget.commandPanel.clear()
                        QTimer.singleShot(1000, self.focus_back)
                        self.getOpponentMoveTimer.start(1000)
                        self.setMoveList(uci_string)
            else:
                self.chessBoard.board_object.pop()
                self.rightWidget.commandPanel.clear()
                print("Cancel!")

        elif len(uci_string) == 4:

            target_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[0].lower()]) - 1
            target_row = int(uci_string[1]) - 1
            dest_col = int(CHESSBOARD_LOCATION_CONVERSION[uci_string[2].lower()]) - 1
            dest_row = int(uci_string[3]) - 1
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

                targetWidget = self.leftWidget.grids[target_col][target_row]
                destWidget = self.leftWidget.grids[dest_col][dest_row]
                self.rightWidget.commandPanel.clear()
                if widgetDragDrop(targetWidget, destWidget):
                    QTimer.singleShot(1000, self.focus_back)
                    self.getOpponentMoveTimer.start(1000)
                    self.setMoveList(uci_string)
                    
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
        
        QTimer.singleShot(500, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.getPiecesLocation, self.getPiecesLocation))

    ##check game end, sync with mirrored chess board and announce opponent's move
    def announceMove(self, sanString):
        print("broadcast move: ", sanString)
        if sanString == None or self.chessBoard == None:
            return False
        crawl_result = None
        check_win = self.chessBoard.detect_win()
        if not check_win == "No win detected.":  ##check user wins
            print(check_win)
            speak(check_win, announce=True)
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
                    speak(crawl_result, True, announce=True)
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
                    announce=True,
                )
                self.rightWidget.opponentBox.setText(
                    "Opponent move: \n" + human_string
                )
                self.game_flow_status = Game_flow_status.user_turn
                if not check_win == "No win detected.":
                    speak(check_win, True, announce=True)
                    self.game_flow_status = Game_flow_status.game_end
                    self.change_main_flow_status(Bot_flow_status.setting_status)
                    self.getOpponentMoveTimer.stop()
                    self.getScoreTimer.start(1000)
                if not crawl_result == None:
                    self.game_flow_status = Game_flow_status.game_end
                    self.change_main_flow_status(Bot_flow_status.setting_status)
                    self.getOpponentMoveTimer.stop()
                    self.getScoreTimer.start(1000)
                    speak(crawl_result, True, announce=True)
                return True
        
        return False

    ##Check whether opponent resigned
    def check_game_end(self):   
        def callback(result):
            if result:
                self.game_flow_status = Game_flow_status.game_end
                self.change_main_flow_status(Bot_flow_status.game_end_status)
                self.getScoreTimer.start(1000)
                self.getOpponentMoveTimer.stop()
                print(result)
                speak(result, announce=True)

        if(self.game_play_mode == Game_play_mode.computer_mode):
            self.leftWidget.chessWebView.page().runJavaScript(js_function.checkGameEnd + 'checkGameEnd("computer");', callback)
        else:
            self.leftWidget.chessWebView.page().runJavaScript(js_function.checkGameEnd + 'checkGameEnd("online");', callback)

    ##JS to get opponent move SAN
    def getOpponentMove(self):
        def callback(x):

            print(f"Opponent move = {x}")
            
            if self.announceMove(x):
                self.getOpponentMoveTimer.stop()
                move = self.chessBoard.board_object.pop()
                self.setMoveList(move)
                self.chessBoard.board_object.push_uci(str(move))
                self.leftWidget.chessWebView.page().runJavaScript(js_function.getPiecesLocation, self.getPiecesLocation)
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

    ##initialize mirror chessboard
    def getBoard(self, *args):
        self.chessBoard = ChessBoard(args[0]) if(args) else ChessBoard()
        self.change_main_flow_status(Bot_flow_status.game_play_status)

    ##toggle the marked square layer -> hide before perfrom click
    def all_grids_switch(self, on_off):
        for i in range(8):
            for j in range(8):
                if on_off:
                    self.leftWidget.grids[i][j].show()
                else:
                    self.leftWidget.grids[i][j].hide()

    ##JS to detect the assigned color
        
    def getColor(self, exist_game = ""):
        def callback(color):
            print(color)
            self.userColor = color
            self.rightWidget.colorBox.setText("Assigned Color: " + color)
            if color == "BLACK":
                self.opponentColor = "WHITE"
                self.row, self.col = 7, 7
                self.currentPos = 'h8'
                speak(exist_game + Speak_template.user_black_side_sentense.value)
                self.game_flow_status = Game_flow_status.opponent_turn
                self.getOpponentMoveTimer.start(1000)
            else:
                self.opponentColor = "BLACK"
                self.row, self.col = 0, 0
                self.currentPos = 'a1'
                speak(exist_game + Speak_template.user_white_side_sentense.value)
                self.game_flow_status = Game_flow_status.user_turn

        self.leftWidget.chessWebView.page().runJavaScript(js_function.getColor, callback)

    #JS to detect grid position and assign label reference
    def initBoard(self):
        def callback(coor):
            print(coor)
            x = coor[0]
            y = coor[1]
            dist = coor[2]
            print(f"INITBOARD COLOR: {self.userColor}")
            if(self.userColor == "WHITE"):
                for row in range(8):
                    for col in range(8):
                        label = QLabel(self)
                        label.setGeometry(int(x + col*dist), int(y - row*dist), int(dist*0.5), int(dist*0.5))
                        pos = list(CHESSBOARD_LOCATION_CONVERSION.keys())[list(CHESSBOARD_LOCATION_CONVERSION.values()).index(str(col+1))] + str(row+1)
                        # label.setText("  " + pos)
                        label.setAccessibleName(pos)
                        label.hide()
                        self.leftWidget.grids[col][row] = label
            else:
                for row in reversed(range(8)):
                    for col in reversed(range(8)):
                        label = QLabel(self)
                        label.setGeometry(int(x + (7-col)*dist), int(y - (7-row)*dist), int(dist*0.5), int(dist*0.5))
                        pos = list(CHESSBOARD_LOCATION_CONVERSION.keys())[list(CHESSBOARD_LOCATION_CONVERSION.values()).index(str(col+1))] + str(row+1)
                        # label.setText("  " + pos)
                        label.setAccessibleName(pos)
                        label.hide()
                        self.leftWidget.grids[col][row] = label

            self.leftWidget.chessWebView.page().runJavaScript(js_function.getPiecesLocation, self.getPiecesLocation)

        self.leftWidget.chessWebView.page().runJavaScript(js_function.getBoard, callback)

    ##switch to command mode
    def switch_command_mode(self):
        print("shortcut ctrl + F pressed")
        speak("command mode <> you can type your move here")
        self.arrow_mode_switch(False)
        self.input_mode = Input_mode.command_mode
        self.currentFocus = len(self.rightWidget.play_menu) - 1
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

            self.setStyleSheet(
                "QLabel:focus { border: 5px solid rgba(255, 0, 0, 1); }"
            )

            self.leftWidget.grids[self.col][self.row].setFocus()

    ##arrow key move and speak the square information
    def handle_arrow(self, direction):
        if not self.main_flow_status == Bot_flow_status.game_play_status:
            return
        # print(self.currentFocus, direction)
        print(f"col: {self.col}, row: {self.row}")
        match direction:
            case 'UP':
                if(self.userColor == "WHITE"):
                    self.row = min(self.row + 1, 7)
                    self.leftWidget.grids[self.col][self.row].setFocus()
                else:
                    self.row = max(self.row - 1, 0)
                    self.leftWidget.grids[self.col][self.row].setFocus()
    
            case 'DOWN':
                if(self.userColor == "WHITE"):
                    self.row = max(self.row - 1, 0)
                    self.leftWidget.grids[self.col][self.row].setFocus()
                else:
                    self.row = min(self.row + 1, 7)
                    self.leftWidget.grids[self.col][self.row].setFocus()

            case 'RIGHT':
                if(self.userColor == "WHITE"):
                    self.col = min(self.col + 1, 7)
                    self.leftWidget.grids[self.col][self.row].setFocus()
                else:
                    self.col = max(self.col - 1, 0)
                    self.leftWidget.grids[self.col][self.row].setFocus()

            case 'LEFT':
                if(self.userColor == "WHITE"):
                    self.col = max(self.col - 1, 0)
                    self.leftWidget.grids[self.col][self.row].setFocus()
                else:
                    self.col = min(self.col + 1, 7)
                    self.leftWidget.grids[self.col][self.row].setFocus()
        # QLabel.setAccessibleDescription("HELLO")
        # QLabel.setAccessibleName("Name")
        self.currentPos = list(CHESSBOARD_LOCATION_CONVERSION.keys())[list(CHESSBOARD_LOCATION_CONVERSION.values()).index(str(self.col+1))] + str(self.row+1)
        piece = self.chessBoard.check_grid(self.currentPos).__str__()
        if piece == "None":
            self.leftWidget.grids[self.col][self.row].setAccessibleName(self.currentPos)
            speak("{0}".format(self.currentPos))
            return
        else:
            color = "white" if piece.isupper() else "black"
            piece_square_text = "{0} {1} {2}".format(
                self.currentPos,
                color,
                PIECE_TYPE_CONVERSION.get(piece.lower()),
            )
            self.leftWidget.grids[self.col][self.row].setAccessibleName(piece_square_text)
            print(piece_square_text)
            speak(piece_square_text)

    ##select the piece under arrow mode
    def handle_space(self):
        if not self.input_mode == Input_mode.arrow_mode:
            return
        if len(self.rightWidget.commandPanel.text()) == 4:
            self.CommandPanelHandler()
            return
        if not self.currentPos == None:
            piece = self.chessBoard.check_grid(self.currentPos).__str__()
            if not piece == "None":
                color = "white" if piece.isupper() else "black"
                piece = PIECE_TYPE_CONVERSION.get(piece.lower())
                speak(color + " " + piece + " selected")

        current_value = self.rightWidget.commandPanel.text()
        self.rightWidget.commandPanel.setText(current_value + self.currentPos)
        if len(self.rightWidget.commandPanel.text()) == 4:
            self.CommandPanelHandler()

    ##clear the selected piece under arrow mode
    def handle_arrow_delete(self):
        if not self.input_mode == Input_mode.arrow_mode:
            return
        self.rightWidget.commandPanel.setText("")

    ##control tab event on right widget
    def handle_tab(self, press):
        if self.input_mode == Input_mode.command_mode:
            unhidden_widgets = []
            # if self.main_flow_status == Bot_flow_status.login_status:
            #     unhidden_widgets = self.rightWidget.login_menu
            if self.game_play_mode == Game_play_mode.analysis_mode:
                unhidden_widgets = self.rightWidget.analysis_menu
                print(len(unhidden_widgets))
            else:
                layout = self.rightWidget.layout()
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if widget and not widget.isHidden():
                        unhidden_widgets.append(widget)
            match press:
                case "UP" | "LEFT":
                    print("up")
                    if int(self.currentFocus - 1) < 0:
                        self.currentFocus = len(unhidden_widgets)-1
                    else:
                        self.currentFocus = self.currentFocus - 1
                case "DOWN" | "RIGHT":
                    print("down")
                    if int(self.currentFocus + 1) >= len(unhidden_widgets):
                        self.currentFocus = 0
                    else:
                        self.currentFocus = self.currentFocus + 1
                case "TAB":
                    print("tab")
                    if int(self.currentFocus + 1) >= len(unhidden_widgets):
                        self.currentFocus = 0
                    else:
                        self.currentFocus = self.currentFocus + 1

            unhidden_widgets[self.currentFocus].setFocus()
            try:
                intro = unhidden_widgets[self.currentFocus].text()
                if intro == "":
                    intro = unhidden_widgets[self.currentFocus].accessibleDescription()
            except:
                index = unhidden_widgets[self.currentFocus].currentIndex()
                intro = "Current Bot: " + unhidden_widgets[self.currentFocus].itemData(index, Qt.ItemDataRole.AccessibleTextRole)
                # intro = unhidden_widgets[self.currentFocus].currentText()
            
            speak(intro)
                        
        else:
            self.leftWidget.grids[self.col][self.row].setFocus()

    ##switch to arrow mode
    def arrow_mode_switch(self, on_off):
        menu = ["MENUUP", "MENUDOWN", "MENULEFT", "MENURIGHT"]
        arrows = ["UP", "DOWN", "LEFT", "RIGHT", "SPACE", "DELETE"]
        boo = False if on_off else True
        for i in menu:
            self.arrow_shortcut.get(i).setEnabled(boo)
        for arrow in arrows:
            self.arrow_shortcut.get(arrow).setEnabled(on_off)


    ##repeat the previous sentence
    def repeat_previous(self):
        speak(previous_sentence)

    ##tell user different options based on the application status
    def helper_menu(self):
        print("helper")
        match self.main_flow_status:
            case Bot_flow_status.setting_status:
                if(self.game_play_mode == Game_play_mode.analysis_mode):
                    speak(Speak_template.analysis_help_message.value)
                else:
                    speak(Speak_template.setting_state_help_message.value)
                return
            case Bot_flow_status.board_init_status:
                speak(Speak_template.init_state_help_message.value)
                return
            case Bot_flow_status.select_status:
                if(Game_flow_status == Game_play_mode.computer_mode):
                    speak(Speak_template.select_computer_help_message.value)
                else:
                    speak(Speak_template.select_online_help_message.value)
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

    def voice_helper_menu(self):
        print("voice helper")
        match self.main_flow_status:
            case Bot_flow_status.setting_status:
                speak(Speak_template.setting_state_vinput_help_message.value)
                return
            case Bot_flow_status.board_init_status:
                speak(Speak_template.init_state_help_message.value)
                return
            case Bot_flow_status.select_status:
                if(Game_flow_status == Game_play_mode.computer_mode):
                    speak(Speak_template.select_computer_vinput_help_message.value)
                else:
                    speak(Speak_template.select_online_vinput_help_message.value)
            case Bot_flow_status.game_play_status:
                if self.input_mode == Input_mode.command_mode:
                    speak(Speak_template.command_panel_vinput_help_message.value)

    def setMoveList(self, move):
        print(f"MOVE = {move} Type = {type(move)}")
        if(isinstance(move, str)):
            if(self.moveList_element % 2 == 0):
                self.moveListString += str(self.moveList_line) + ". " + move.lower() + ", "
            else:
                self.moveListString += move.lower() + ", "
                self.moveList_line += 1
        else:
            if(self.moveList_element % 2 == 0):
                self.moveListString += str(self.moveList_line) + ". " + self.chessBoard.board_object.parse_san(str(move)).uci() + ", "
            else:
                self.moveListString += self.chessBoard.board_object.parse_san(str(move)).uci() + ", "
                self.moveList_line += 1
            
        if(self.moveList_element % 10 == 0 and self.moveList_element != 0):
                self.moveListString += "\n"
        self.moveList_element += 1

        self.rightWidget.moveList.setText("Move List:\n" + self.moveListString)

    def __init__(self, *args, **kwargs):

        self.settings = QSettings('ChessBot', 'config')
        print(self.settings.fileName())


        print(f"rate: {speak_thread.rate}")
        print(f"volume: {speak_thread.volume}")
        
        global previous_sentence
        
        self.restoreConfig()

        self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.number = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.chess_position = [a + b for a in [x.lower() for x in self.alphabet] for b in self.number]
        self.moveListString = ""
        self.moveList_line = 1
        self.moveList_element = 0
        self.FenNotation = ""
        self.userLoginName = ""
        self.previous_game_exist = False
        self.boardDescription = []
        self.whiteLoc = []
        self.blackLoc = []
        self.timeControl = ""
        self.category_combobox = None
        self.bot_retry = False

        super(MainWindow, self).__init__(*args, **kwargs)

        shortcut_F = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_F.activated.connect(self.switch_command_mode)

        shortcut_J = QShortcut(QKeySequence("Ctrl+J"), self)
        shortcut_J.activated.connect(self.switch_arrow_mode)

        shortcut_S = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_S.activated.connect(self.voice_input)

        shortcut_menu_up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        shortcut_menu_up.activated.connect(lambda: self.handle_tab("UP"))

        shortcut_menu_down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        shortcut_menu_down.activated.connect(lambda: self.handle_tab("DOWN"))
        
        shortcut_menu_left = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_menu_left.activated.connect(lambda: self.handle_tab("LEFT"))

        shortcut_menu_right = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_menu_right.activated.connect(lambda: self.handle_tab("RIGHT"))

        shortcut_arrow_UP = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        shortcut_arrow_UP.activated.connect(partial(self.handle_arrow, "UP"))

        shortcut_arrow_DOWN = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        shortcut_arrow_DOWN.activated.connect(partial(self.handle_arrow, "DOWN"))

        shortcut_arrow_LEFT = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        shortcut_arrow_LEFT.activated.connect(partial(self.handle_arrow, "LEFT"))

        shortcut_arrow_RIGHT = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        shortcut_arrow_RIGHT.activated.connect(partial(self.handle_arrow, "RIGHT"))

        shortcut_SPACE = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        shortcut_SPACE.activated.connect(self.handle_space)

        shortcut_DELETE = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self)
        shortcut_DELETE.activated.connect(self.handle_arrow_delete)

        shortcut_TAB = QShortcut(QKeySequence(Qt.Key.Key_Tab), self)
        shortcut_TAB.activated.connect(lambda: self.handle_tab("TAB"))

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

        shortcut_ctrlp = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut_ctrlp.activated.connect(self.voice_helper_menu)

        self.shortcut_A = QShortcut(QKeySequence("a"), self)
        self.shortcut_A.activated.connect(self.analysisModeHandler)
        
        self.arrow_shortcut = {
            "MENUUP": shortcut_menu_up,
            "MENUDOWN": shortcut_menu_down,
            "MENULEFT": shortcut_menu_left,
            "MENURIGHT": shortcut_menu_right,
            "UP": shortcut_arrow_UP,
            "DOWN": shortcut_arrow_DOWN,
            "LEFT": shortcut_arrow_LEFT,
            "RIGHT": shortcut_arrow_RIGHT,
            "SPACE": shortcut_SPACE,
            "DELETE": shortcut_DELETE,
        }

        self.arrow_mode_switch(False)

        # analysis_Shortcut_UP = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        # analysis_Shortcut_UP.activated.connect(self.analysis_FirstMove)

        analysis_Shortcut_LEFT = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        analysis_Shortcut_LEFT.activated.connect(self.analysis_PreviousMove)

        analysis_Shortcut_RIGHT = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        analysis_Shortcut_RIGHT.activated.connect(self.analysis_NextMove)

        analysis_Shortcut_BestMove = QShortcut(QKeySequence("b"), self)
        analysis_Shortcut_BestMove.activated.connect(self.analysis_BestMove)

        analysis_Shortcut_Explanation = QShortcut(QKeySequence("e"), self)
        analysis_Shortcut_Explanation.activated.connect(self.analysis_Explanation)

        analysis_Shortcut_CurrentMove = QShortcut(QKeySequence("c"), self)
        analysis_Shortcut_CurrentMove.activated.connect(self.analysis_CurrentMove)

        self.analysis_Shortcut = {
            "B": analysis_Shortcut_BestMove,
            "E": analysis_Shortcut_Explanation,
            "C": analysis_Shortcut_CurrentMove,
            "LEFT": analysis_Shortcut_LEFT,
            "RIGHT": analysis_Shortcut_RIGHT,
        }

        self.analysis_mode_switch(False)

        shortcut_q = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut_q.activated.connect(self.chatbot)

        ##initialize flow status
        self.main_flow_status = Bot_flow_status.setting_status
        self.game_flow_status = Game_flow_status.not_start
        self.input_mode = Input_mode.command_mode
        self.game_play_mode = None

        ##initialize UI components
        self.mainWidget = QWidget()
        self.leftWidget = LeftWidget()
        self.rightWidget = RightWidget()
        self.chatbotWidget = ChatbotWindow()

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
        self.rightWidget.check_being_attacked.clicked.connect(
            self.macroView
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

        self.rightWidget.nextPuzzleButton.clicked.connect(self.clickNextPuzzle)

        self.rightWidget.retryPuzzleButton.clicked.connect(self.retryPuzzle)

        self.rightWidget.resign.clicked.connect(self.resign_handler)

        self.rightWidget.loginButton.clicked.connect(lambda: self.change_main_flow_status(Bot_flow_status.login_status))

        self.rightWidget.chatbot_button.clicked.connect(self.chatbot)

        self.rightWidget.commandPanel.returnPressed.connect(self.CommandPanelHandler)
        self.rightWidget.check_position.returnPressed.connect(
            self.check_position_handler
        )

        self.rightWidget.loginAccount_Input.returnPressed.connect(self.loginHandler)
        self.rightWidget.loginPassword_Input.returnPressed.connect(self.loginHandler)
        self.rightWidget.login_button.pressed.connect(self.loginHandler)

        self.rightWidget.selectPanel.returnPressed.connect(self.selectPanelHandler)

        self.leftWidget.chessWebView.loadFinished.connect(self.checkLogined)

        self.leftWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.getScoreTimer = QTimer()
        self.getScoreTimer.timeout.connect(self.check_score)

        self.getOpponentMoveTimer = QTimer()
        self.getOpponentMoveTimer.timeout.connect(self.getOpponentMove)

        self.check_game_end_timer = QTimer()
        self.check_game_end_timer.timeout.connect(self.check_game_end)

        self.cooldownTimer = QTimer()
        self.cooldownTimer.timeout.connect(self.reset_cooldown)
        self.cooldown = False

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
        # self.rightWidget.playWithComputerButton.setFocus()
        self.currentFocus = 0
        # self.show_information_box()

        self.rightWidget.settingButton.clicked.connect(self.openSettingMenu)

        self.rightWidget.playWithOther_Bullet_1_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_1_0.value))
        self.rightWidget.playWithOther_Bullet_1_1_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_1_1.value))
        self.rightWidget.playWithOther_Bullet_2_1_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_2_1.value))

        self.rightWidget.playWithOther_Blitz_3_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_3_0.value))
        self.rightWidget.playWithOther_Blitz_3_2_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_3_2.value))
        self.rightWidget.playWithOther_Blitz_5_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_5_0.value))

        self.rightWidget.playWithOther_Rapid_10_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_10_0.value))
        self.rightWidget.playWithOther_Rapid_15_10_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_15_10.value))
        self.rightWidget.playWithOther_Rapid_30_0_Button.clicked.connect(lambda: self.online_select_timeControl(timeControl.timeControl_30_0.value))

## bot category
        self.rightWidget.playWithComputerButton_Coach.clicked.connect(lambda: self.bot_select_category("coach"))
        self.rightWidget.playWithComputerButton_Adaptive.clicked.connect(lambda: self.bot_select_category("adaptive"))
        self.rightWidget.playWithComputerButton_Beginner.clicked.connect(lambda: self.bot_select_category("beginner"))
        self.rightWidget.playWithComputerButton_Intermediate.clicked.connect(lambda: self.bot_select_category("intermediate"))
        self.rightWidget.playWithComputerButton_Advanced.clicked.connect(lambda: self.bot_select_category("advanced"))
        self.rightWidget.playWithComputerButton_Master.clicked.connect(lambda: self.bot_select_category("master"))
        self.rightWidget.playWithComputerButton_Athletes.clicked.connect(lambda: self.bot_select_category("athletes"))
        self.rightWidget.playWithComputerButton_Musicians.clicked.connect(lambda: self.bot_select_category("musicians"))
        self.rightWidget.playWithComputerButton_Creators.clicked.connect(lambda: self.bot_select_category("creators"))
        self.rightWidget.playWithComputerButton_TopPlayers.clicked.connect(lambda: self.bot_select_category("top_players"))
        self.rightWidget.playWithComputerButton_Personalities.clicked.connect(lambda: self.bot_select_category("personalities"))
        self.rightWidget.playWithComputerButton_Engine.clicked.connect(lambda: self.bot_select_category("engine"))
        self.rightWidget.back_to_category_button.clicked.connect(self.back_to_category)
        self.rightWidget.play_button.clicked.connect(self.select_bot)

        self.rightWidget.combobox_coach.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_coach.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_adaptive.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_adaptive.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_beginner.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_beginner.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_intermediate.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_intermediate.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_advanced.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_advanced.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_master.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_master.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_athletes.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_athletes.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_musicians.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_musicians.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_creators.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_creators.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_top_players.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_top_players.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_personalities.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_personalities.highlighted.connect(self.bot_information)

        self.rightWidget.combobox_engine.currentIndexChanged.connect(lambda index: self.bot_information(index, select=True))
        self.rightWidget.combobox_engine.highlighted.connect(self.bot_information)

## analysis mode button connection
        self.rightWidget.gamereviewButton.clicked.connect(self.analysisModeHandler)
        self.rightWidget.analysis_NextMove_Button.clicked.connect(self.analysis_NextMove)
        self.rightWidget.analysis_PreviousMove_Button.clicked.connect(self.analysis_PreviousMove)
        self.rightWidget.analysis_FirstMove_Button.clicked.connect(self.analysis_FirstMove)
        self.rightWidget.analysis_BestMove_Button.clicked.connect(self.analysis_BestMove)
        # self.rightWidget.analysis_Explanation_Button.clicked.connect(self.analysis_Explanation)
        # self.rightWidget.analysis_CurrentMove_Button.clicked.connect(self.analysis_CurrentMove)
        # self.rightWidget.analysis_LastMove_Button.clicked.connect(self.analysis_LastMove)

        self.rightWidget.newgameButton.clicked.connect(self.newGame)
        self.rightWidget.returnToHomePageButton.clicked.connect(self.returnHomePage)

        voice_input_thread.action_signal.connect(self.check_action) #receive voice input signal
        self.chatbotWidget.action_signal.connect(self.check_action) 

## restore user settings
    def restoreConfig(self):
        global internal_speak_engine
        speak_thread.setRateValue(int(self.settings.value('rate', 200)))    # Restore User Config
        speak_thread.setVolumeValue(float(self.settings.value('volume', 0.7)))
        internal_speak_engine = bool(self.settings.value('speak_engine', True))

## store user settings
    def closeEvent(self, event):
        global internal_speak_engine
        self.settings.setValue('rate', str(speak_thread.getRateValue()))
        self.settings.setValue('volume', str(speak_thread.getVolumeValue()))
        self.settings.setValue('speak_engine', '1' if internal_speak_engine else '')

## handle start a new game
    def newGame(self):
        timeControl = self.timeControl
        game_play_mode = self.game_play_mode
        print(f"time control = {timeControl}")
        self.change_main_flow_status(Bot_flow_status.setting_status)
        match(game_play_mode):
            case Game_play_mode.computer_mode:
                print("Restart Computer Game")
                speak("Restart Computer Game")
                self.leftWidget.chessWebView.page().runJavaScript(js_function.bot_new_game)
                self.change_main_flow_status(Bot_flow_status.board_init_status)
                self.getColor()
                self.initBoard()
                self.getBoard()
                self.change_main_flow_status(Bot_flow_status.game_play_status)

            case Game_play_mode.online_mode:
                print("Starting a new game")
                speak("Starting a new game")
                self.check_action(timeControl)

## back to main phase (game mode selection)
    def returnHomePage(self):
        if(self.game_play_mode == Game_play_mode.analysis_mode):
            self.keyPressed_Signal.disconnect(self.analysisAction)
            self.shortcut_A.activated.connect(self.analysisModeHandler)
            self.analysis_mode_switch(False)
        self.leftWidget.chessWebView.load(QUrl("https://www.chess.com"))
        self.change_main_flow_status(Bot_flow_status.setting_status)
        speak("You have returned to home page")

## function to announce the pieces being attacked
    def macroView(self):
        self.exist_square = []
        black = ["q", "n", "r", "b","p","k"]
        white = ["Q", "N", "R", "B","P","K"]
        result = ""
        match(self.userColor):
            case "WHITE":
                for square in chess.SQUARES:
                    piece = self.chessBoard.board_object.piece_at(square)
                    if piece is not None and str(piece) in white:
                        self.exist_square.append(square)
                for i in self.exist_square:
                    piece = self.chessBoard.board_object.piece_at(i)
                    if self.chessBoard.board_object.is_attacked_by(chess.BLACK, i):
                        print(f"Piece {PIECES_SHORTFORM_CONVERTER[piece.symbol()]} at square {chess.SQUARE_NAMES[i]} is being attacked")
                        result += (f"Piece {PIECES_SHORTFORM_CONVERTER[piece.symbol()]} at square {chess.SQUARE_NAMES[i]} is being attacked.\n")
            case "BLACK":
                for square in chess.SQUARES:
                    piece = self.chessBoard.board_object.piece_at(square)
                    if piece is not None and str(piece) in black:
                        self.exist_square.append(square)
                for i in self.exist_square:
                    piece = self.chessBoard.board_object.piece_at(i)
                    if self.chessBoard.board_object.is_attacked_by(chess.WHITE, i):
                        print(f"Piece {PIECES_SHORTFORM_CONVERTER[piece.symbol()]} at square {chess.SQUARE_NAMES[i]} is being attacked")
                        result += (f"Piece {PIECES_SHORTFORM_CONVERTER[piece.symbol()]} at square {chess.SQUARE_NAMES[i]} is being attacked")
        if(result == ""):
            speak("No pieces are under attack")
        else:
            speak(result)

## display chatbot interface
    def chatbot(self):
            self.chatbotWidget.show()
            speak("Hello! I am a Chat Bot. How can I help you today? Type in your question and I will answer immediately. You can type in how to use for help.")
    
## handle setting menu
    def openSettingMenu(self):
        global internal_speak_engine
        menu = SettingMenu(rate=int((speak_thread.getRateValue() - 100) * 0.5), volume=int(speak_thread.getVolumeValue() * 100), engine=internal_speak_engine)
        print(f"rate: {speak_thread.getRateValue()}, volume: {speak_thread.getVolumeValue()}")
        # menu.speech_rate_slider.setValue()
        # menu.speech_volume_slider.setValue()

        if menu.exec():
            self.speech_rate = menu.get_rate_value() * 2 + 100  # change to scale of interval 100 to 300
            self.speech_volume = menu.get_volume_value()
            internal_speak_engine = menu.get_engine_value()
            speak_thread.setRateValue(self.speech_rate)
            speak_thread.setVolumeValue(self.speech_volume)

## Game Review Function
    def analysisModeHandler(self):
        def setMoveLength(length):
            self.moveLength = length
            print(f"moveLength = {self.moveLength}")

        def callback0(x):
            QTimer.singleShot(500, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.getGameId, callback1))

        def callback1(gameId):
            print(gameId)
            self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(3000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.checkReviewLimited, callback2)))
            if(self.game_play_mode == Game_play_mode.computer_mode):
                self.leftWidget.chessWebView.load(QUrl(f"https://www.chess.com/analysis/game/computer/{gameId}"))
            else:
                self.leftWidget.chessWebView.load(QUrl(f"https://www.chess.com/analysis/game/live/{gameId}"))

        def callback2(ReviewLimited):
            print(f"Reivew Limited: {ReviewLimited}")
            self.leftWidget.chessWebView.loadFinished.disconnect()
            if(ReviewLimited):
                print("You have used your free Game Review for the day.")
                speak("You have used your free Game Review for the day.")
                self.shortcut_A.activated.connect(self.analysisModeHandler)
            else:
                # self.leftWidget.key_signal.connect(self.analysisAction)
                self.analysis_mode_switch(True)
                self.keyPressed_Signal.connect(self.analysisAction)
                self.leftWidget.chessWebView.page().runJavaScript(js_function.clickStartReview, callback3)
                self.change_game_mode(Game_play_mode.analysis_mode)

        def callback3(value):
            if(value == None):
                QTimer.singleShot(1000, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.clickStartReview, callback3))
            else:
                callback4(value)

        def callback4(comment):
            QTimer.singleShot(300, lambda: self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_GetMoveLength, setMoveLength))
            self.leftWidget.chessWebView.setFocus()
            self.gameReviewMode_Reader(comment)

        def checkLogin(button):
            if(button != None):
                print("Please login for Game Review Function")
                speak("Please login for Game Review Function")
                return
            self.shortcut_A.activated.disconnect()
            self.bestExist = False
            self.analysisCount = 0
            self.keyPressed = None
            self.analysisBoard = ChessBoard()
            self.moveLength = -1
            self.best_pressed = False
            self.leftWidget.chessWebView.page().runJavaScript(js_function.clickGameReview, callback0)
        
        # if(self.game_flow_status != Game_flow_status.game_end):
        #     print("No finished game for analysis")
        #     speak("No finished game for analysis")
        #     return
        self.leftWidget.chessWebView.page().runJavaScript(js_function.checkLogin, checkLogin)
        


    def gameReviewMode_Reader(self, comment):
        print(comment)
        if(isinstance(comment, list)):
            self.feedback = comment[0]
            self.explain = comment[1]
            self.bestExist = comment[2]
            print(f"Signal: {self.keyPressed_Signal}, Left: {Qt.Key.Key_Left}")
            print(f"analysis Count: {self.analysisCount}")
            if(self.keyPressed == Qt.Key.Key_Left):
                if(self.analysisCount==0):
                    self.analysisBoard.board_object.pop()
                else:
                    self.analysisBoard.board_object.pop()
                    self.analysisBoard.board_object.pop()

            print(f"Board: {self.analysisBoard.board_object}")
            sanString = self.feedback.split(" ")[0].strip()
            print(f"sanstring: {sanString}")
            # self.rightWidget.analysisCurrentMove.setText("Current Move: \n" + sanString + ", ")
            print(f"feedback: {self.feedback}")
            self.feedback = self.feedback.replace(sanString, self.analysisHumanForm(self.feedback))
            if(self.best_pressed):
                self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_retry)
                self.analysisBoard.board_object.pop()
                self.best_pressed = False
            if(self.explain != None):
                self.rightWidget.analysisExplanation.setText("Explanation: \n" + self.explain)
            else:
                self.rightWidget.analysisExplanation.setText("Explanation: No content")
        else:
            if(self.keyPressed == Qt.Key.Key_Left):
                self.analysisBoard.board_object.pop()
            self.feedback = comment
            self.rightWidget.analysisCurrentMove.setText("Current Move: This is the beginning")

        print(self.analysisBoard.board_object)
        self.rightWidget.analysisComment.setText("Game Review Comment: \n" + self.feedback)
        print(self.feedback)
        speak(self.feedback)

    def gameReviewMode_Explainer(self):
        print(self.explain)
        speak(self.explain)

    def getReviewComment(self):
        self.leftWidget.chessWebView.page().runJavaScript(js_function.getReviewComment, self.gameReviewMode_Reader)

    def analysisAction(self, key):
        if(self.game_play_mode == Game_play_mode.analysis_mode):
            print(f"key: {key}")
            match key:
                case Qt.Key.Key_Left:
                    self.keyPressed = Qt.Key.Key_Left
                    if(self.analysisCount == 0):
                        speak("This is the beginning")
                    else:
                        self.analysisCount -= 1
                        QTimer.singleShot(300, self.getReviewComment)
                        
                case Qt.Key.Key_Right:
                    self.keyPressed = Qt.Key.Key_Right
                    if(self.analysisCount == self.moveLength):
                        speak("This the last move")
                    else:
                        self.analysisCount += 1
                        QTimer.singleShot(300, self.getReviewComment)

                case Qt.Key.Key_Up:
                    self.keyPressed = Qt.Key.Key_Up
                    self.analysisCount = 0
                    self.analysisBoard = ChessBoard()
                    print(self.analysisBoard)
                    QTimer.singleShot(300, self.getReviewComment)

                # case Qt.Key.Key_Down:
                #     QTimer.singleShot(300, self.getReviewComment)

                case Qt.Key.Key_E:
                    self.keyPressed = Qt.Key.Key_E
                    self.gameReviewMode_Explainer()

                case Qt.Key.Key_B:
                    if(self.bestExist):
                        self.keyPressed = Qt.Key.Key_B
                        self.best_pressed = True
                        self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_GetBestMove)
                        self.poppedMove = self.analysisBoard.board_object.pop()
                        QTimer.singleShot(1000, self.getReviewComment)
                    else:
                        print("The current move is the best move")
                        speak("The current move is the best move")

                case Qt.Key.Key_C:
                    speak(self.rightWidget.analysisCurrentMove.text())

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

        if(self.keyPressed == Qt.Key.Key_B):
            self.analysisBoard.board_object.push(self.poppedMove)
            self.keyPressed = None
            self.best_pressed = True
            print(self.analysisBoard)
        else:
            self.analysisBoard.board_object.push_san(sanString)

        self.rightWidget.analysisCurrentMove.setText(("Current Move: \n" + result))
        return result
    
    def analysis_NextMove(self):
        if (self.cooldown == True):
            return
        self.cooldown = True
        self.cooldownTimer.start(500)
        self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_NextMove)
        QTimer.singleShot(100, lambda: self.keyPressed_Signal.emit(Qt.Key.Key_Right))

    def analysis_PreviousMove(self):
        if (self.cooldown == True):
            return
        self.cooldown = True
        self.cooldownTimer.start(500)
        self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_PreviousMove)
        QTimer.singleShot(100, lambda: self.keyPressed_Signal.emit(Qt.Key.Key_Left))

    def analysis_FirstMove(self):
        if (self.cooldown == True):
            return
        self.cooldown = True
        self.cooldownTimer.start(500)
        self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_FirstMove)
        QTimer.singleShot(100, lambda: self.keyPressed_Signal.emit(Qt.Key.Key_Up))

    # def analysis_LastMove(self):
    #     self.leftWidget.chessWebView.page().runJavaScript(js_function.analysis_LastMove)
    #     QTimer.singleShot(300, lambda: self.keyPressed_Signal.emit(Qt.Key.Key_Down))

    def analysis_BestMove(self):
        if (self.cooldown == True):
            return
        self.cooldown = True
        self.cooldownTimer.start(500)
        QTimer.singleShot(100, lambda: self.keyPressed_Signal.emit(Qt.Key.Key_B))

    def analysis_Explanation(self):
        self.keyPressed_Signal.emit(Qt.Key.Key_E)

    def analysis_CurrentMove(self):
        self.keyPressed_Signal.emit(Qt.Key.Key_C)

    def reset_cooldown(self):
        self.cooldown = False
        self.cooldownTimer.stop()

    def analysis_mode_switch(self, on_off):
        menu = ["MENULEFT", "MENURIGHT"]
        array = ["LEFT", "RIGHT", "B", "E", "C"]
        boo = False if on_off else True
        for item in menu:
            self.arrow_shortcut.get(item).setEnabled(boo)
        for item in array:
            self.analysis_Shortcut.get(item).setEnabled(on_off)

## Game Review Function End

## Voice Input Function

    def voice_input(self):
        print("Ctrl S is pressed")
        if not voice_input_thread.press_event.is_set():
            voice_input_thread.press_event.set()
            print("Voice Input activated. Listening...")
            speak("Voice Input activated. Listening...")
        else:
            voice_input_thread.press_event.clear()
            print("Voice input End")
            speak("Voice input end")

    def check_action(self, str):
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
                    self.puzzle_movePiece(voice_input_thread.chess_move)
                else:
                    self.movePiece(voice_input_thread.chess_move)
            case "resign":
                self.resign_handler()
            case _:
                if (self.game_flow_status != Bot_flow_status.select_status and self.game_flow_status != Bot_flow_status.game_play_status):
                    self.game_play_mode = Game_play_mode.online_mode
                    layout = self.rightWidget.layout()
                    unhidden_widgets = []
                    for i in range(layout.count()):
                        widget = layout.itemAt(i).widget()
                        if widget and not widget.isHidden():
                            unhidden_widgets.append(widget)
                    for item in unhidden_widgets:
                        item.hide()
                    self.leftWidget.chessWebView.loadFinished.connect(lambda: QTimer.singleShot(2000, lambda: self.online_select_timeControl(str, skip=True)))
                    self.leftWidget.chessWebView.load(QUrl("https://www.chess.com/play/online"))
                else:
                    self.online_select_timeControl(str)

    def currentOption(self):
        match self.main_flow_status:
            case Bot_flow_status.setting_status:
                print("Choose the game mode that you want to play")

    def keyPressEvent(self, event):
        key = event.key()
        if(key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_E, Qt.Key.Key_B)):
            self.keyPressed_Signal.emit(event.key())
    
## load text to TTS queue
def speak(sentence, importance=False, dialog=False, announce=None):
    global previous_sentence
    global internal_speak_engine

    previous_sentence = sentence
    if internal_speak_engine:
        speak_thread.queue.put((sentence, importance))
    else:
        print("no speak engine")
        if(announce):
            print("announce move")
            speak_thread.queue.put((sentence, importance))

# Voice Input Thread to handle audio recording, speech-to-text, keyword extraction and trigger signals
class VoiceInput_Thread(QThread):
    '''
    Allow User using Voice Input by record user's audio, perform Speech to Text and
    determine which action to perform based on the text result
    '''

    action_signal = pyqtSignal(str)

    ##auto start and loop until application close
    def __init__(self):
        super(VoiceInput_Thread, self).__init__()

        self.press_event = Event()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model("./small.en.pt", device=device)
        
        self.text_output = ""
        self.daemon = True
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.frames = []
        self.chess_move = []
        self.start()
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK)

    def run(self):
        while True:
            self.press_event.wait()
            if self.press_event.is_set():
                self.record()

    def record(self):
        print("Voice Input function running")
        while self.press_event.is_set():
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
            print("Speech to Text performing...")
            self.text_output = self.model.transcribe("./tmp.wav", fp16=False, env=my_env)["text"].lower()
            print(f"Speech to Text finished! Output: {self.text_output}")
            self.checkAction()

        self.frames = []
        # self.stream.stop_stream()
        # self.stream.close()
        # self.audio.terminate()

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
                    print("Sorry, I don't understand your request. Please repeat it again")
                    speak("Sorry, I don't understand your request. Please repeat it again")
                    # self.action_signal.emit()
                case Game_play_mode.online_mode:
                    find = False
                    for item in timeControlDeterminant_Speak:
                        if (find == True):
                            break
                        for words in item.value:
                            if(words in self.text_output):
                                print(f"Time Control: {item.value[words]}")
                                self.action_signal.emit(item.value[words])
                                find = True
                                break
                    if(find == False):
                        print("Invalid Input. Please try again")
                        speak("Invalid Input. Please try again")
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
            speak("Sorry, I don't understand your request. Please repeat it again")

    def voiceToMove(self):
        self.chess_move = []
        self.chess_order = []
        for moves in window.chess_position:
            if moves in self.text_output:
                self.chess_move.append(moves)
                self.chess_order.append(self.text_output.find(moves))
                print(f"move: {moves}")
        print(f"chess move = {self.chess_move}")
        if(len(self.chess_move)==2):
            print(self.chess_move[0], self.chess_move[1])
            if(self.chess_order[0]<self.chess_order[1]):
                self.chess_move = "".join(self.chess_move[0] + self.chess_move[1])
            else:
                self.chess_move = "".join(self.chess_move[1] + self.chess_move[0])
            print(f"chess move: {self.chess_move}")
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

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        ffmpeg_dir = os.path.join(os.path.dirname(sys.executable), 'ffmpeg', 'bin')
        my_env = os.environ
        my_env['PATH'] = f"{ffmpeg_dir}{os.pathsep}{my_env['PATH']}"
    else:
        ffmpeg_dir = os.path.join(current_dir, 'ffmpeg', 'bin')
        my_env = os.environ
        my_env['PATH'] = f"{ffmpeg_dir}{os.pathsep}{my_env['PATH']}"

    # print(my_env)

    app = QApplication(sys.argv)
    app.setApplicationName("Chess Bot")

    window = MainWindow()


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
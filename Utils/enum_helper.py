from enum import Enum


class Game_play_mode(Enum):
    computer_mode = "COMPUTER_MODE"
    online_mode = "ONLINE_MODE"
    puzzle_mode = "PUZZLE_MODE"


class Input_mode(Enum):
    command_mode = "COMMAND_MODE"
    arrow_mode = "ARROW_MDOE"


class Bot_flow_status(Enum):
    setting_status = "SETTING_STATUS"
    select_status = "SELECT_STATUS"
    board_init_status = "BOARD_INIT_STATUS"
    game_play_status = "GAME_PLAY_STATUS"


class Game_flow_status(Enum):
    # sub-routine of game play status
    not_start = "NOT_START"
    user_turn = "USER_TURN"
    opponent_turn = "OPPONENT_TURN"
    game_end = "GAME_END"


class Speak_template(Enum):
    ###setting
    welcome_sentense = "Welcome to chess bot!! "
    game_intro_sentense = "you can press control O to find the options. <> press control R to repeat last sentence"
    setting_state_help_message = (
        "tab and choose play with computer engine or other online player"
    )

    ###initialization
    initialize_game_sentense = "Initializing game for you"
    init_state_help_message = "please wait the initializing process"

    ###game play
    game_state_help_message = (
        "You can press control F for command mode or press control J for arrow mode"
    )
    command_panel_help_message = (
        "tab to find other functions <> or press control J for arrow mode"
    )

    arrow_mode_help_message = "use arrow key to travel the chess board <> use space bar to select the piece to move <> and the square to place <>"

    opponent_move_sentense = "{0} {1} moved to {2} "

    ask_for_promote_type = "please indicate promote type by first letter"
    confirm_move = "Confirm move {0} to {1} "
    user_resign = "Resigned"
    check_time_sentense = "you remain {0}, opponent remain {1}"

    user_black_side_sentense = (
        "You are playing as black. Please wait for your opponent's move."
    )
    user_white_side_sentense = "You are playing as white. Please make your first move."



class english_chess_pieces_name(Enum):
    King = "king"
    Queen = "queen"
    Bishop = "bishop"
    Rook = "rook"
    Knight = "knight"
    Pawn = "pawn"

class bot_List(Enum):

    backToSchool_ChadThaddeusBradley = {"name": "Chad Thaddeus Bradley", "rating": "575", "cat": "Back To School"} #tick
    backToSchool_StanleyFunk = {"name": "Stanley Funk", "rating": "1065", "cat": "Back To School"} #tick
    backToSchool_BaileyHoops = {"name": "Bailey Hoops", "rating": "1450", "cat": "Back To School"} #tick
    backToSchool_ProfessorPassant = {"name": "Professor Passant", "rating": "2025", "cat": "Back To School"} #tick
    backToSchool_Eugene = {"name": "Eugene", "rating": "?", "cat": "Back To School"} #tick

    coach_CoachDanny = {"name": "Coach Danny", "rating": "400", "cat": "Coach"} #tick
    coach_CoachMae = {"name": "Coach Mae", "rating": "800", "cat": "Coach"} #tick
    coach_CoachDante = {"name": "Coach Dante", "rating": "1200", "cat": "Coach"}
    coach_CoachMonica = {"name": "Coach Monica", "rating": "1600", "cat": "Coach"} 
    coach_CoachDavid = {"name": "Coach David", "rating": "2000", "cat": "Coach"}

    adaptive_Jimmy = {"name": "Jimmy", "rating": "600", "cat": "Adaptive"}  #tick
    adaptive_Nisha = {"name": "Nisha", "rating": "900", "cat": "Adaptive"}
    adaptive_Tomas = {"name": "Tomas", "rating": "1200", "cat": "Adaptive"}
    adaptive_Devon = {"name": "Devon", "rating": "1600", "cat": "Adaptive"}
    adaptive_Natasha = {"name": "Natasha", "rating": "2000", "cat": "Adaptive"}

    beginner_Martin = {"name": "Martin", "rating": "250", "cat": "Beginner"} #tick
    beginner_Wayne = {"name": "Wayne", "rating": "250", "cat": "Beginner"}
    beginner_Fabian = {"name": "Fabian", "rating": "250", "cat": "Beginner"}
    beginner_Juan = {"name": "Juan", "rating": "400", "cat": "Beginner"}
    beginner_Filip = {"name": "Filip", "rating": "400", "cat": "Beginner"}
    beginner_Elani = {"name": "Elani", "rating": "400", "cat": "Beginner"} #tick
    beginner_Noel = {"name": "Noel", "rating": "550", "cat": "Beginner"}
    beginner_Oliver = {"name": "Oliver", "rating": "550", "cat": "Beginner"}
    beginner_Milica = {"name": "Milica", "rating": "550", "cat": "Beginner"}
    beginner_Aron = {"name": "Aron", "rating": "700", "cat": "Beginner"}
    beginner_Janjay = {"name": "Janjay", "rating": "700", "cat": "Beginner"} #tick
    beginner_Mina = {"name": "Mina", "rating": "700", "cat": "Beginner"}
    beginner_Zara = {"name": "Zara", "rating": "850", "cat": "Beginner"}
    beginner_Santiago = {"name": "Santiago", "rating": "850", "cat": "Beginner"}
    beginner_Karim = {"name": "Karim", "rating": "850", "cat": "Beginner"}

    intermediate_Maria = {"name": "Maria", "rating": "1000", "cat": "Intermediate"} #tick
    intermediate_Maxim = {"name": "Maxim", "rating": "1000", "cat": "Intermediate"}
    intermediate_Hans = {"name": "Hans", "rating": "1000", "cat": "Intermediate"}
    intermediate_Azeez = {"name": "Azeez", "rating": "1100", "cat": "Intermediate"}
    intermediate_Laura = {"name": "Laura", "rating": "1100", "cat": "Intermediate"}
    intermediate_Sven = {"name": "Sven", "rating": "1100", "cat": "Intermediate"} #tick
    intermediate_Emir = {"name": "Emir", "rating": "1200", "cat": "Intermediate"}
    intermediate_Elena = {"name": "Elena", "rating": "1200", "cat": "Intermediate"}
    intermediate_Wilson = {"name": "Wilson", "rating": "1200", "cat": "Intermediate"}
    intermediate_Vinh = {"name": "Vinh", "rating": "1300", "cat": "Intermediate"}
    intermediate_Nelson = {"name": "Nelson", "rating": "1300", "cat": "Intermediate"} #tick
    intermediate_Jade = {"name": "Jade", "rating": "1300", "cat": "Intermediate"}
    intermediate_David = {"name": "David", "rating": "1400", "cat": "Intermediate"}
    intermediate_Ali = {"name": "Ali", "rating": "1400", "cat": "Intermediate"}
    intermediate_Mateo = {"name": "Mateo", "rating": "1400", "cat": "Intermediate"}

    advanced_Wendy = {"name": "Wendy", "rating": "1500", "cat": "Advanced"} #tick
    advanced_Antonio = {"name": "Antonio", "rating": "1500", "cat": "Advanced"}
    advanced_Pierre = {"name": "Pierre", "rating": "1500", "cat": "Advanced"}
    advanced_Pablo = {"name": "Pablo", "rating": "1600", "cat": "Advanced"}
    advanced_Joel = {"name": "Joel", "rating": "1600", "cat": "Advanced"}
    advanced_Isabel = {"name": "Isabel", "rating": "1600", "cat": "Advanced"} #tick
    advanced_Arthur = {"name": "Arthur", "rating": "1700", "cat": "Advanced"}
    advanced_Jonas = {"name": "Jonas", "rating": "1700", "cat": "Advanced"}
    advanced_Isla = {"name": "Isla", "rating": "1700", "cat": "Advanced"}
    advanced_Lorenzo = {"name": "Lorenzo", "rating": "1800", "cat": "Advanced"}
    advanced_Wally = {"name": "Wally", "rating": "1800", "cat": "Advanced"} #tick
    advanced_Julia = {"name": "Julia", "rating": "1800", "cat": "Advanced"}
    advanced_Miguel = {"name": "Miguel", "rating": "1900", "cat": "Advanced"}
    advanced_Xavier = {"name": "Xavier", "rating": "1900", "cat": "Advanced"}
    advanced_Olga = {"name": "Olga", "rating": "1900", "cat": "Advanced"}
    advanced_Li = {"name": "Li", "rating": "2000", "cat": "Advanced"} #tick
    advanced_Charles = {"name": "Charles", "rating": "2000", "cat": "Advanced"}
    advanced_Fatima = {"name": "Fatima", "rating": "2000", "cat": "Advanced"}
    advanced_Manuel = {"name": "Manuel", "rating": "2100", "cat": "Advanced"}
    advanced_Oscar = {"name": "Oscar", "rating": "2100", "cat": "Advanced"}

    master_Nora = {"name": "Nora", "rating": "2200", "cat": "Master"} #tick
    master_Noam = {"name": "Noam", "rating": "2200", "cat": "Master"}
    master_Ahmed = {"name": "Ahmed", "rating": "2200", "cat": "Master"}
    master_Sakura = {"name": "Sakura", "rating": "2200", "cat": "Master"}
    master_Arjun = {"name": "Arjun", "rating": "2300", "cat": "Master"}
    master_Francis = {"name": "Francis", "rating": "2300", "cat": "Master"} #tick
    master_Sofia = {"name": "Sofia", "rating": "2300", "cat": "Master"}
    master_Alexander = {"name": "Alexander", "rating": "2450", "cat": "Master"}
    master_Luke = {"name": "Luke", "rating": "2450", "cat": "Master"}
    master_Wei = {"name": "Wei", "rating": "2450", "cat": "Master"}

    athletes_LarryFitzgeraldJr = {"name": "Larry Fitzgerald Jr.", "rating": "1250", "cat": "Athletes"} #tick
    athletes_JaylenBrown = {"name": "Jaylen Brown", "rating": "1500", "cat": "Athletes"} #tick
    athletes_GordonHayward = {"name": "Gordon Hayward", "rating": "1350", "cat": "Athletes"} #tick
    athletes_ChidobeAwuzie = {"name": "Chidobe Awuzie", "rating": "1400", "cat": "Athletes"} #tick
    athletes_ChristianPulisic = {"name": "Christian Pulisic", "rating": "1500", "cat": "Athletes"} #tick
    athletes_DarylMorey = {"name": "Daryl Morey", "rating": "1550", "cat": "Athletes"} #tick
    athletes_LukAI = {"name": "Luk.AI", "rating": "2500", "cat": "Athletes"} #tick

    musicians_ThomasMars = {"name": "Thomas Mars", "rating": "1500", "cat": "musicians"} #tick
    musicians_Wallows = {"name": "Wallows", "rating": "1200", "cat": "musicians"} #tick

    engine_Beginner_Rating250 = {"name": "Beginner", "rating": "250", "cat": "Engine"}

class timeControl(Enum):
    timeControl_1_0 = "1 min"
    timeControl_1_1 = "1 | 1"
    timeControl_2_1 = "2 | 1"
    timeControl_3_0 = "3 min"
    timeControl_3_2 = "3 | 2"
    timeControl_5_0 = "5 min"
    timeControl_10_0 = "10 min"
    timeControl_15_10 = "15 | 10"
    timeControl_30_0 = "30 min"

class determinant(Enum):
    options_words = ["option", "options"]

    computer_mode_words = ["computer", "computers", "pvc", "bot", "bots"]

    online_mode_words = ["online", "player", "players", "pvp", "rank"]

    puzzle_mode_words = ["puzzle", "puzzles"]

    resign_words = ["resign", "give up", "forfeit", "surrender"]

    quit_application_words = ["quit", "exit", "leave", "close", "shutdown"]

class timeControlDeterminant(Enum):
    timeControl_1_0_words = dict.fromkeys(["1+0", "1 + 0", "1|0", "1 | 0", "1 min", "1min", "one minute", "1 minute", "1minute", "1 plus 0"], timeControl.timeControl_1_0.value)
    timeControl_1_1_words = dict.fromkeys(["1+1", "1 + 1", "1|1", "1 | 1", "one plus one", "1 plus 1", "one + one"], timeControl.timeControl_1_1.value)
    timeControl_2_1_words = dict.fromkeys(["2+1", "2 + 1", "2|1", "2 | 1", "two plus one", "2 plus 1", "two + one"], timeControl.timeControl_2_1.value)
    timeControl_3_0_words = dict.fromkeys(["3+0", "3 + 0", "3|0", "3 | 0", "3 min", "3min", "three minute", "3 minute", "3minute", "3 plus 0"], timeControl.timeControl_3_0.value)
    timeControl_3_2_words = dict.fromkeys(["3+2", "3 + 2", "3|2", "3 | 2", "three plus two", "3 plus 2", "three + two"], timeControl.timeControl_3_2.value)
    timeControl_5_0_words = dict.fromkeys(["5+0", "5 + 0", "5|0", "5 | 0", "5 min", "5min", "five minute", "5 minute", "5minute", "5 plus 0"], timeControl.timeControl_5_0.value)
    timeControl_10_0_words = dict.fromkeys(["10+0", "10 + 0", "10|0", "10 | 0", "10 min", "10min", "ten minute", "10 minute", "10minute", "10 plus 0"], timeControl.timeControl_10_0.value)
    timeControl_15_10_words = dict.fromkeys(["15+10", "15 + 10", "15|10", "15 | 10", "fifteen plus ten", "15 plus 10", "fifteen + ten"], timeControl.timeControl_15_10.value)
    timeControl_30_0_words = dict.fromkeys(["30+0", "30 + 0", "30|0", "30 | 0", "30 min", "30min", "thirty minute", "30 minute", "30minute", "30 plus 0", "default"], timeControl.timeControl_10_0.value)

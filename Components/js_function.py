white_GetOpponentMove = """
    function getOpponentMove(mode) {
        let player_color = "WHITE";
        let moveList = document.querySelectorAll(".main-line-row");
        let opponent_move;
        let black_icon = "";
        let lastMove = moveList[moveList.length-1];
        let info = lastMove?.textContent.trim().split("   ");
        if(document?.querySelector('[data-move-list-el]')){
            info.splice(info.length-1, 1);
        }
        if(info.length!=3){
            opponent_move = null;
        }
        else{
            let chessIcon = lastMove.querySelectorAll(".icon-font-chess");
            if(chessIcon.length>0){
                if(chessIcon.length==1){
                    if(chessIcon[0].getAttribute("class").includes("black")){
                        black_icon = chessIcon[0].getAttribute("data-figurine");
                    }
                }
                else{
                    black_icon = chessIcon[1].getAttribute("data-figurine");
                }
            }
            opponent_move = black_icon + info[2].trim();
        }
        return opponent_move;
    }
    getOpponentMove();
    """

black_GetOpponentMove = """
    function getOpponentMove(mode) {
        let player_color = "BLACK";
        let moveList = document.querySelectorAll(".main-line-row");
        let opponent_move;
        let white_icon = "";
        let lastMove = moveList[moveList.length-1];
        let info = lastMove.textContent.trim().split("   ");
        if(document?.querySelector('[data-move-list-el]')){
            info.splice(info.length-1, 1);
        }
        if(info.length==3){
            opponent_move = null;    
        }
        else{
            let chessIcon = lastMove.querySelectorAll(".icon-font-chess")
            if(chessIcon.length>0){
                if(chessIcon.length==1){
                    if(chessIcon[0].getAttribute("class").includes("white")){
                        white_icon = chessIcon[0].getAttribute("data-figurine");
                    }
                }
                else{
                    white_icon = chessIcon[0].getAttribute("data-figurine");
                }
            }
        opponent_move = white_icon + info[1].trim();
        }
        return opponent_move;  
    }
    getOpponentMove();
    """

checkGameEnd = """
    function checkGameEnd(mode){
        let moveList = document.querySelectorAll(".main-line-row");
        if(moveList[moveList.length-1].outerHTML.includes("result")){
            if(mode == 'computer'){
                return document.querySelector('.modal-game-over-header-component').textContent.trim();
            }
            else{
                return document.querySelector('.game-over-header-header').textContent.trim();
            }
        }
        return false;
    }
"""

getFEN = """
    function getFEN(){
        let FEN = document.querySelector(".share-menu-tab-pgn-section").getElementsByClassName("ui_v5-input-component")[0]._value;
        document.querySelector('[aria-label="Close"]').click();
        return FEN;
    }
    getFEN();
"""

checkExistGame = """
    function checkExistGame() {
        let moveList = document.querySelectorAll(".main-line-row");
        if(moveList.length>0){
            let move = [];
            for(let i = 0; i<moveList.length; i++){
                let white_icon = "";
                let black_icon = "";
                let info = moveList[i].textContent.trim().split("    ");
                if(document?.querySelector('[data-move-list-el]')){
                    info.splice(info.length-1, 1);
                }
                let chessIcon = moveList[i].querySelectorAll(".icon-font-chess");
                if(info.length==2){
                    if(chessIcon.length>0){
                        white_icon = chessIcon[0].getAttribute("data-figurine");
                    }
                    move.push(white_icon + info[1].trim());
                }
                else{
                    if(chessIcon.length>0){
                        if(chessIcon.length==1){
                            if(chessIcon[0].getAttribute("class").includes("white")){
                                white_icon = chessIcon[0].getAttribute("data-figurine");
                            }
                            else{
                                black_icon = chessIcon[0].getAttribute("data-figurine");
                            }
                        }
                        else{
                            white_icon = chessIcon[0].getAttribute("data-figurine");
                            black_icon = chessIcon[1].getAttribute("data-figurine");
                        }                 
                    }
                    move.push(white_icon + info[1].trim());
                    move.push(black_icon + info[2].trim());
                }
            }
            return move;
        }
        return false;
    }
    checkExistGame();
    """
puzzle_mode_constructBoard = """
    function puzzle_mode_constructBoard(){
        notation_transform_dictionary = {
            "bq":"q",
            "bk":"k",
            "bn":"n",
            "bb":"b",
            "br":"r",
            "bp":"p",
            "wq":"Q",
            "wk":"K",
            "wn":"N",
            "wb":"B",
            "wr":"R",
            "wp":"P",
        }
        let pieces = document.querySelectorAll(".piece");
        let board_element = Array.from(Array(8), _ => Array(8).fill(0));
        for(let i=0; i<pieces.length; i++){
            let info = pieces[i].getAttribute("class");
            let location = info.match(/\d+/)[0];
            info = info.split(" ")
            let piece_type = notation_transform_dictionary[info[1]];
            if(piece_type==null){
                piece_type = notation_transform_dictionary[info[2]];
            }
            board_element[location[1]-1][location[0]-1] = piece_type;
        }
        return board_element;
    }
    puzzle_mode_constructBoard();
    """


puzzle_mode_GetTitle = """
    function puzzle_mode_GetTitle(){
        document?.querySelector(".modal-first-time-button")?.getElementsByTagName('button')[0].click();
        let title = document?.querySelector(".section-heading-title")?.textContent?.split(' ')[0];
        if(title == null){
            title = document.querySelector(".cc-text-speech-bold").textContent.split(' ')[0]
        }
        return title;
    }
    puzzle_mode_GetTitle();
"""

puzzle_mode_GetOpponentMove = """
    function puzzle_mode_GetOpponentMove(){
        let position_transform_dictionary = {
            "1":"A",
            "2":"B",
            "3":"C",
            "4":"D",
            "5":"E",
            "6":"F",
            "7":"G",
            "8":"H",
        }
        let pos1 = document.querySelectorAll(".highlight")[0].getAttribute("class").split(' ')[1].match(/\d+/)[0];
        let pos2 = document.querySelectorAll(".highlight")[1].getAttribute("class").split(' ')[1].match(/\d+/)[0];
        pos1 = position_transform_dictionary[[pos1[0]]] + pos1[1];
        pos2 = position_transform_dictionary[pos2[0]] + pos2[1];
        return pos1 + pos2;
    }
    puzzle_mode_GetOpponentMove();
"""

getCoordinate = """
    function getCoordinate(pos, screen_left, screen_top){
        let pix_scale = window.devicePixelRatio;
        let top_margin = window.outerHeight - window.innerHeight;
        let pieces = document.querySelector(".square-" + pos);
        let info = pieces.getBoundingClientRect();
        let interval = info['height'];
        let win_x = (window.screenX - screen_left);
        let win_y = (window.screenY - screen_top);
        let x = ((info['left'] + info['right']) * 0.5  + win_x) * pix_scale + screen_left;
        let y = ((info['top'] + info['bottom']) * 0.5 + win_y + top_margin) * pix_scale + screen_top;
        let name = pieces.getAttribute('class'); 
        return [x, y, interval*pix_scale, name, pix_scale];
}
"""
## pix_scale 計返放大嘅比例, 用作計算正確coordinate
## top margin 用作移動鼠標到程式內容的左上角(不是視窗)
## 解決多mon錯位嘅問題: 搵返目前視窗處於嘅位置, 拎佢嘅left同top value,
# 將現有嘅coordinate_x減去left, coordinate_x減去top 再乘以倍大比例去獲取移位後嘅coordinate, 最後加返減去嘅top同left將鼠標移去正面嘅monitor

clickNextPuzzle = """
    function clickNextPuzzle(){
        let target = document.querySelector('[aria-label="Next Puzzle"]');
        target.click();
    }
    clickNextPuzzle();
    """

clickTimeControlButton = """
    function clickTimeControlButton(timeControl, login){
        document.querySelector('.selector-button-button').click();
        setTimeout(() => {
            let buttons = document.querySelectorAll('button');
            for(button of buttons){
                if(button?.textContent?.trim()?.toLowerCase() == timeControl){
                    button.click();
                    break;
                }
            }
            setTimeout(() => {
                document.querySelector('.cc-button-primary').click();
                if(!login){
                    setTimeout(() => document.querySelector('.authentication-intro-guest').click(), 500);
                }
                else{
                    setTimeout(() => document.querySelector(".fair-play-button").click(), 500);
                }
            }, 1000)
        }, 500);
    }
"""

clickShare = """
    function clickShare(){
        document.querySelector('[aria-label="Share"]').click();
        setTimeout(() => {
            document.querySelector('.share-menu-tab-selector-tab').click();
        }, 300);
    }
    clickShare();
"""

checkMoveSuccess = """
    function checkMoveSuccess(targetSrc){
        pieces = document.querySelectorAll(".piece")
        for(piece of pieces){
            if(piece.getAttribute("class").includes("square-"+ targetSrc)){
                return false;
            }
        }
        return true;
    }
"""

clickGameReview = """
    function clickGameReview(){
        for(let i of document?.querySelectorAll('button')){
            console.log(i.textContent.trim().toLowerCase())
            if(i.textContent.trim().toLowerCase() == "game review"){
                i.click();
                return true;
            }
        }
        return false;
    }
    clickGameReview();
"""

getGameId = """
    function getGameId(){
        return document.URL.match(/\d+/)[0] //game id
    }
    getGameId();
"""

clickStartReview = """
    function clickStartReview(){
        if(document.querySelector('.cc-button-primary') == null){
            return null;
        }
        let overview = document.querySelector(".bot-speech-content-content-container").textContent;
        document.querySelector('.cc-button-primary').click();
        setTimeout(() => {
            document.querySelector('[aria-label="First Move"]').click();            
        }, 300);
        return overview;
    }
    clickStartReview();
"""

checkReviewLimited = """
    function checkReviewLimited(){
        if(document.querySelector('.modal-upgrade-game-review-limit')){
            return true;
        }
        return false;
    }
    checkReviewLimited();
"""

getReviewComment = """
    function getReviewComment(){
        let selected = document.querySelector(".selected");
        if(selected != null){
            let icon = selected?.querySelector('.icon-font-chess')?.getAttribute('data-figurine');
            if(icon == null){
                icon = "";
            }
            let feedback = document.querySelector(".move-feedback-box-move").textContent.trim();
            if(feedback.includes("=")){
                let index = feedback.indexOf("is");
                let lastSeq = feedback.substring(index, feedback.length);
                feedback = selected.textContent + lastSeq; 
            }
            else{
                feedback = icon + feedback;   
            }
            let explain = document.querySelector('.analysis-type-component')?.textContent;
            let bestExist = false;
            if(document.querySelector('.perfect')){
                bestExist = true;
            }
            return [feedback, explain, bestExist];
        }
        return document.querySelector(".bot-speech-content-content-container").textContent.trim();
    }
    getReviewComment();
"""

analysis_GetBestMove = """
    function analysis_GetBestMove(){
        document.querySelector('.perfect').click();
    }
    analysis_GetBestMove();
"""

analysis_GetMoveLength = """
    function analysis_GetMoveLength(){
        return document.querySelectorAll('.main-line-ply').length;
    }
    analysis_GetMoveLength();
"""

userLogin = """
    function userLogin(username, password){
        let usernameField = document.querySelector('[aria-label="Username or Email"]');
        usernameField.value = username;
        usernameField.dispatchEvent(new Event('input', { bubbles: true }));
        usernameField.dispatchEvent(new Event('change', { bubbles: true }));
        
        let passwordField = document.querySelector('[aria-label="Password"]');
        passwordField.value = password;
        passwordField.dispatchEvent(new Event('input', { bubbles: true }));
        passwordField.dispatchEvent(new Event('change', { bubbles: true }));
        
        document.querySelector('[name="_remember_me"]').click();
        setTimeout(document.querySelector('[name="login"]').click(), 500);
    }
"""

loginSuccess = """
    function loginSuccess(){
        if(document.querySelector('[name="login"]') == null){
            return true;
        }
        return false;
    }
    loginSuccess();
"""

analysis_NextMove = """
    function analysis_NextMove(){
        document.querySelector('[aria-label="Next Move"]').click()
    }
    analysis_NextMove();
"""

analysis_PreviousMove = """
    function analysis_PreviousMove(){
        document.querySelector('[aria-label="Previous Move"]').click()
    }
    analysis_PreviousMove();
"""

analysis_FirstMove = """
    function analysis_FirstMove(){
        document.querySelector('[aria-label="First Move"]').click()
    }
    analysis_FirstMove();
"""    

analysis_LastMove = """
    function analysis_LastMove(){
        document.querySelector('[aria-label="Last Move"]').click()
    }
    analysis_LastMove();
"""
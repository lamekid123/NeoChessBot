white_GetOpponentMove = f"""
    function getOpponentMove() {{
        let player_color = "WHITE";
        let moveList = document.querySelectorAll(".main-line-row");
        let LastMove;
        let info;
        let opponent_move;
        let black_icon = ""
        if(moveList[moveList.length-1].outerHTML.includes("result")){{
            return "game end";
        }}
        lastMove = moveList[moveList.length-1];
        info = lastMove.textContent.trim().split("    ");
        if(info.length!=3){{
            opponent_move = null;
        }}
        else{{
            let chessIcon = lastMove.querySelectorAll(".icon-font-chess");
            if(chessIcon.length>0){{
                if(chessIcon.length==1){{
                    if(chessIcon[0].getAttribute("class").includes("black")){{
                        black_icon = chessIcon[0].getAttribute("data-figurine");
                    }}
                }}
                else{{
                    black_icon = chessIcon[1].getAttribute("data-figurine");
                }}
            }}
            opponent_move = black_icon + info[2].trim();
        }}
        return opponent_move;  
    }}
    getOpponentMove();
    """
##親自開chess.com console嚟搵邊個file有move
##做乜: 喺啲html code入面拎current board嘅last move. 然後佢懶係野咁將啲棋嘅字轉做icon onj, 所以又要加多幾行去check佢係咩icon然後轉返做字


black_GetOpponentMove = f"""
    function getOpponentMove() {{
        let player_color = "BLACK";
        let moveList = document.querySelectorAll(".main-line-row");
        let LastMove;
        let info;
        let opponent_move;
        let white_icon = ""
        if(moveList[moveList.length-1].outerHTML.includes("result")){{
            lastMove = moveList[moveList.length-2];
        }}
        lastMove = moveList[moveList.length-1];
        info = lastMove.textContent.trim().split("    "); 
        if(info.length==3){{
            opponent_move = null;    
        }}
        else{{
            let chessIcon = lastMove.querySelectorAll(".icon-font-chess")
            if(chessIcon.length>0){{
                if(chessIcon.length==1){{
                    if(chessIcon[0].getAttribute("class").includes("white")){{
                        white_icon = chessIcon[0].getAttribute("data-figurine");
                    }}
                }}
                else{{
                    white_icon = chessIcon[0].getAttribute("data-figurine");
                }}
            }}
        opponent_move = white_icon + info[1].trim();
        }}
        return opponent_move;  
    }}
    getOpponentMove();
    """

check_ExistGame = f"""
    function check_ExistGame() {{
        let moveList = document.querySelectorAll(".main-line-row");
        if(moveList.length>0){{
            let move = [];
            for(let i = 0; i<moveList.length; i++){{
                let white_icon = "";
                let black_icon = "";
                let info = moveList[i].textContent.trim().split("    ");
                let chessIcon = moveList[i].querySelectorAll(".icon-font-chess");
                if(info.length==2){{
                    if(chessIcon.length>0){{
                        white_icon = chessIcon[0].getAttribute("data-figurine");
                    }}
                    move.push(white_icon + info[1].trim());
                }}
                else{{
                    if(chessIcon.length>0){{
                        if(chessIcon.length==1){{
                            if(chessIcon[0].getAttribute("class").includes("white")){{
                                white_icon = chessIcon[0].getAttribute("data-figurine");
                            }}
                            else{{
                                black_icon = chessIcon[0].getAttribute("data-figurine");
                            }}
                        }}
                        else{{
                            white_icon = chessIcon[0].getAttribute("data-figurine");
                            black_icon = chessIcon[1].getAttribute("data-figurine");
                        }}                 
                    }}
                    move.push(white_icon + info[1].trim());
                    move.push(black_icon + info[2].trim());
                }}
            }}
            return move;
        }}
        return false;
    }}
    check_ExistGame();
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
        let board = document.querySelector(".board");
        let pieces = board.querySelectorAll(".piece");
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
        return document.querySelector(".section-heading-title").textContent.split(' ')[0];
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
        let board = document.querySelector(".board");
        let pieces = board.querySelector(".square-" + pos);
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

clickNextPuzzle = """
    function clickNextPuzzle(){
        let target = document.querySelector('[aria-label="Next Puzzle"]');
        target.click();
    }
    clickNextPuzzle();
    """
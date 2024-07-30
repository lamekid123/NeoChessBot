White_getOpponentMove = f"""
    function getOpponentMove() {{
        let player_color = "WHITE";
        let moveList = document.querySelectorAll('.main-line-row');
        let LastMove;
        let info;
        let opponent_move;
        if(moveList[moveList.length-1].outerHTML.includes('result')){{
            LastMove = moveList[moveList.length-2];
        }}
        LastMove = moveList[moveList.length-1];
        if(player_color=="WHITE"){{
            info = LastMove.textContent.trim().split('    ');
            if(info.length!=3){{
                opponent_move = null;
            }}
            else{{
                opponent_move = info[2];
            }}
        }}
        else if(player_color=="BLACK"){{
            info = LastMove.textContent.trim().split('    '); 
            if(info.length==3){{
                opponent_move = null;    
            }}
            opponent_move = info[1];
        }}
        console.log(opponent_move);
        return opponent_move;  
    }}
    getOpponentMove();
    """
##親自開chess.com console嚟搵邊個file有move


Black_getOpponentMove = f"""
    function getOpponentMove() {{
        let player_color = "BLACK";
        let moveList = document.querySelectorAll('.main-line-row');
        let LastMove;
        let info;
        let opponent_move;
        if(moveList[moveList.length-1].outerHTML.includes('result')){{
            LastMove = moveList[moveList.length-2];
        }}
        LastMove = moveList[moveList.length-1];
        if(player_color=="WHITE"){{
            info = LastMove.textContent.trim().split('    ');
            if(info.length!=3){{
                opponent_move = null;
            }}
            else{{
                opponent_move = info[2];
            }}
        }}
        else if(player_color=="BLACK"){{
            info = LastMove.textContent.trim().split('    '); 
            if(info.length==3){{
                opponent_move = null;    
            }}
            opponent_move = info[1];
        }}
        console.log(opponent_move);
        return opponent_move;  
    }}
    getOpponentMove();
    """
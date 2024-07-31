White_getOpponentMove = f"""
    function getOpponentMove() {{
        let player_color = "WHITE";
        let moveList = document.querySelectorAll('.main-line-row');
        let LastMove;
        let info;
        let opponent_move;
        let black_icon = ""
        if(moveList[moveList.length-1].outerHTML.includes('result')){{
            return 'game end';
        }}
        lastMove = moveList[moveList.length-1];
        info = lastMove.textContent.trim().split('    ');
        if(info.length!=3){{
            opponent_move = null;
        }}
        else{{
            let chessIcon = lastMove.querySelectorAll('.icon-font-chess');
            if(chessIcon.length>0){{
                if(chessIcon.length==1){{
                    if(chessIcon[0].getAttribute('class').includes('black')){{
                        black_icon = chessIcon[0].getAttribute('data-figurine');
                    }}
                }}
                else{{
                    black_icon = chessIcon[1].getAttribute('data-figurine');
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


Black_getOpponentMove = f"""
    function getOpponentMove() {{
        let player_color = "BLACK";
        let moveList = document.querySelectorAll('.main-line-row');
        let LastMove;
        let info;
        let opponent_move;
        let white_icon = ""
        if(moveList[moveList.length-1].outerHTML.includes('result')){{
            lastMove = moveList[moveList.length-2];
        }}
        lastMove = moveList[moveList.length-1];
        let chessIcon = lastMove.querySelectorAll('.icon-font-chess';)
        info = lastMove.textContent.trim().split('    '); 
        if(info.length==3){{
            opponent_move = null;    
        }}
        else{{
            let chessIcon = lastMove.querySelectorAll('.icon-font-chess';)
            if(chessIcon.length>0){{
                if(chessIcon.length==1){{
                    if(chessIcon[0].getAttribute('class').includes('white')){{
                        white_icon = chessIcon[0].getAttribute('data-figurine');
                    }}
                }}
                else{{
                    white_icon = chessIcon[0].getAttribute('data-figurine');
                }}
            }}
        opponent_move = white_icon + info[1].trim();
        }}
        return opponent_move;  
    }}
    getOpponentMove();
    """
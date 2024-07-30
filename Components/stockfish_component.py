from stockfish import Stockfish

class stockfish_adviser():
    def __init__(self):    
        self.stockfish = Stockfish(path="./stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2")
        # stockfish.set_fen_position("RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr b KQkq - 0 2")

    def suggested_move(self):   
            self.best_move = self.stockfish.get_best_move()
            self.src = self.best_move[0] + self.best_move[1]
            self.dest = self.best_move[2] + self.best_move[3]
            self.piece_on_src = str(self.stockfish.get_what_is_on_square(self.src)).split('_')[1]
            self.piece_on_dest = self.stockfish.get_what_is_on_square(self.dest)
            if(self.piece_on_dest==None):
                return f"The best move is to move the {self.piece_on_src} on {self.src} to {self.dest}"
            else:
                self.piece_on_dest = str(self.piece_on_dest).split('_')[1]
                return f"The best move is to move the {self.piece_on_src} on {self.src} to capture the {self.piece_on_dest} on {self.dest}"

    def reference_move(self, move):
        if(self.stockfish.is_move_correct(move)==True):
            self.stockfish.make_moves_from_current_position([move])
            print(self.stockfish.get_board_visual())
        else:
             print("Invalid move, please try again")
        # print(stockfish.get_wdl_stats())

# a = stockfish_adviser()
# while(True):
#      print(a.suggested_move())
#      a.reference_move(input("enter\n"))
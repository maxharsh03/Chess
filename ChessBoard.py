import itertools
import pygame as p
from copy import deepcopy
p.init()


class Board:
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.board_copy = deepcopy(self.board)
        self.white_turn = True
        self.flag = False
        self.white_check = False
        self.black_check = False
        self.white_king_moved = False
        self.black_king_moved = False
        self.left_white_rook = False
        self.right_white_rook = False
        self.left_black_rook = False
        self.right_black_rook = False
        self.white_left_castle_move = False
        self.white_right_castle_move = False
        self.black_left_castle_move = False
        self.black_right_castle_move = False
        self.white_en_passant = False
        self.black_en_passant = False
        self.checkmate = False
        self.stalemate = False
        self.valid_move = []
        self.actual_move = []
        self.previous_move = ()
        self.new_coordinates = ()
        self.white_pieces = ["wR", "wB", "wN", "wK", "wQ", "wp"]

    # main move function that will call other move functions based on piece type
    def move(self, coordinates, white):
        # passed in as (x, y)
        # before a piece can move we need to check if it is valid
        x = coordinates[0]
        y = coordinates[1]

        self.flag = False
        
        # quickly handles castling moves
        if self.board[y][x] == "wK" or self.board[y][x] == "bK":
            self.castle(coordinates, white)

        if white:
            self.flag = True
            self.move_helper(coordinates, x, y, white, self.board)

            if self.verify_checkmate(white):
                self.checkmate = True
                print("White has been checkmated")
            if self.verify_stalemate(white):
                self.stalemate = True
                print("Stalemate, white has no legal moves and is not in check")

        else:
            self.flag = True
            self.move_helper(coordinates, x, y, white, self.board)

            if self.verify_checkmate(white):
                self.checkmate = True
                print("Black has been checkmated")
            if self.verify_stalemate(white):
                self.stalemate = True
                print("Stalemate, black has no legal moves and is not in check")

    def move_helper(self, coord, x, y, white, board_type):
        if board_type[y][x] == "wp" or board_type[y][x] == "bp":
            self.pawn_move(coord, x, y, white, board_type)
        if board_type[y][x] == "wR" or board_type[y][x] == "bR":
            self.rook_move(coord, x, y, white, board_type)
        if board_type[y][x] == "wN" or board_type[y][x] == "bN":
            self.knight_move(coord, x, y, white, board_type)
        if board_type[y][x] == "wB" or board_type[y][x] == "bB":
            self.bishop_move(coord, x, y, white, board_type)
        if board_type[y][x] == "wQ" or board_type[y][x] == "bQ":
            self.queen_move(coord, x, y, white, board_type)
        if board_type[y][x] == "wK" or board_type[y][x] == "bK":
            self.king_move(coord, x, y, white, board_type)

    # makes move on board
    def make_move(self, m_list, white_turn):
        # handle non-castle moves first (will also move king for castle move but not rook)
        self.board[m_list[1][1]][m_list[1][0]] = self.board[m_list[0][1]][m_list[0][0]]
        self.board[m_list[0][1]][m_list[0][0]] = "--"

        # stuff required for en passant        
        self.previous_move = ()
        self.new_coordinates = ()
        self.previous_move = ((self.board[m_list[1][1]][m_list[1][0]]), abs(m_list[1][1]-m_list[0][1]), white_turn)
        self.new_coordinates = (m_list[1][0], m_list[1][1]) 

        # handles en passant move
        if self.white_en_passant:
            self.board[m_list[1][1]-1][m_list[1][0]] = "--"
            self.white_en_passant = False
        elif self.black_en_passant:
            self.board[m_list[1][1]+1][m_list[1][0]] = "--"
            self.black_en_passant = False

        # handles rook move if king castles
        if self.white_left_castle_move:
            self.board[7][3] = self.board[7][0]
            self.board[7][0] = "--"
            self.white_left_castle_move = False
        elif self.white_right_castle_move:
            self.board[7][5] = self.board[7][7]
            self.board[7][7] = "--"
            self.white_right_castle_move = False
        elif self.black_left_castle_move:
            self.board[0][3] = self.board[0][0]
            self.board[0][0] = "--"
            self.black_left_castle_move = False
        elif self.black_right_castle_move:
            self.board[0][5] = self.board[0][7]
            self.board[0][7] = "--"
            self.black_right_castle_move = False

        # checks if king and rooks have been moved
        if white_turn:
            if self.board[7][4] != "wK":
                self.white_king_moved = True
            if self.board[7][0] != "wR":
                self.left_white_rook = True
            if self.board[7][7] != "wR":
                self.right_white_rook = True
        else: 
            if self.board[0][4] != "bK":
                self.black_king_moved = True
            if self.board[0][0] != "bR":
                self.left_black_rook = True
            if self.board[0][7] != "bR":
                self.right_black_rook = True

        # handles pawn promotion after a move is made
        if white_turn:
            for j in range(8):
                if self.board[0][j] == "wp":
                    self.pawn_promotion(j, 0, white_turn)
        else:
            for j in range(8):
                if self.board[7][j] == "bp":
                    self.pawn_promotion(j, 7, white_turn)

        # resets lists of moves and board copy
        self.valid_move = []
        self.actual_move = []
        self.board_copy = deepcopy(self.board)

    # checks whose turn it currently is
    def turn(self, coordinates):
        if self.board[coordinates[1]][coordinates[0]] in self.white_pieces:
            return True

    # helper functions

    # finds valid pawn moves
    def pawn_move(self, coord, x, y, is_white_turn, board_type):
        if is_white_turn:
            if y == 6:  # have to check if first move
                if board_type[y-1][x] == "--":
                    if self.flag and self.future_check(coord, x, y-1, is_white_turn):
                        self.actual_move.append((x, y-1))
                    elif not self.flag:
                        self.valid_move.append((x, y-1))
                if board_type[y-2][x] == "--":
                    if self.flag and self.future_check(coord, x, y-2, is_white_turn):
                        self.actual_move.append((x, y-2))
                    elif not self.flag:
                        self.valid_move.append((x, y - 2))
                if y-1 > 0 and x-1 > 0 and self.capture(x-1, y-1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x-1, y-1, is_white_turn):
                        self.actual_move.append((x-1, y-1))
                    elif not self.flag:
                        self.valid_move.append((x-1, y - 1))
                if y-1 > 0 and x+1 < 7 and self.capture(x+1, y-1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x+1, y-1, is_white_turn):
                        self.actual_move.append((x+1, y-1))
                    elif not self.flag:
                        self.valid_move.append((x+1, y - 1))
            elif y == 3: # check for en passant 
                if y-1 >= 0 and board_type[y-1][x] == "--":
                    if self.flag and self.future_check(coord, x, y-1, is_white_turn):
                        self.actual_move.append((x, y-1))
                    elif not self.flag:
                        self.valid_move.append((x, y - 1))
                if x == 0 and self.board[y][x+1] == "bp":
                    self.en_passant(coord, x, y, is_white_turn)
                elif x == 7 and self.board[y][x-1] == "bp":
                    self.en_passant(coord, x, y, is_white_turn)
                elif self.board[y][x-1] == "bp" or self.board[y][x+1] == "bp":
                    self.en_passant(coord, x, y, is_white_turn)
            else:
                # checks for captures
                if y-1 >= 0 and board_type[y-1][x] == "--":
                    if self.flag and self.future_check(coord, x, y-1, is_white_turn):
                        self.actual_move.append((x, y-1))
                    elif not self.flag:
                        self.valid_move.append((x, y - 1))
                if y-1 >= 0 and x-1 >= 0 and self.capture(x-1, y-1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x-1, y-1, is_white_turn):
                        self.actual_move.append((x-1, y-1))
                    elif not self.flag:
                        self.valid_move.append((x-1, y-1))
                if y-1 >= 0 and x+1 <= 7 and self.capture(x+1, y-1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x+1, y-1, is_white_turn):
                        self.actual_move.append((x+1, y-1))
                    elif not self.flag:
                        self.valid_move.append((x + 1, y - 1))

        else:
            if y == 1:  # have to check if first move
                if board_type[y+1][x] == "--":
                    if self.flag and self.future_check(coord, x, y+1, is_white_turn):
                        self.actual_move.append((x, y+1))
                    elif not self.flag:
                        self.valid_move.append((x, y + 1))
                if board_type[y+2][x] == "--":
                    if self.flag and self.future_check(coord, x, y+2, is_white_turn):
                        self.actual_move.append((x, y+2))
                    elif not self.flag:
                        self.valid_move.append((x, y + 2))
                if y + 1 < 8 and x - 1 >= 0 and self.capture(x - 1, y + 1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x-1, y+1, is_white_turn):
                        self.actual_move.append((x-1, y+1))
                    elif not self.flag:
                        self.valid_move.append((x - 1, y + 1))
                if y + 1 < 8 and x + 1 <= 7 and self.capture(x + 1, y + 1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x+1, y+1, is_white_turn):
                        self.actual_move.append((x + 1, y + 1))
                    elif not self.flag:
                        self.valid_move.append((x + 1, y + 1))
            elif y == 4: # check for en passant
                if y+1 < 8 and board_type[y+1][x] == "--":
                    if self.flag and self.future_check(coord, x, y+1, is_white_turn):
                        self.actual_move.append((x, y+1))
                    elif not self.flag:
                        self.valid_move.append((x, y + 1)) 
                if x == 0 and self.board[y][x+1] == "wp":
                    self.en_passant(coord, x, y, is_white_turn)
                elif x == 7 and self.board[y][x-1] == "wp":
                    self.en_passant(coord, x, y, is_white_turn)
                elif self.board[y][x-1] == "wp" or self.board[y][x+1] == "wp":
                    self.en_passant(coord, x, y, is_white_turn)
            else:
                # checks for captures
                if y+1 < 8 and board_type[y+1][x] == "--":
                    if self.flag and self.future_check(coord, x, y+1, is_white_turn):
                        self.actual_move.append((x, y+1))
                    elif not self.flag:
                        self.valid_move.append((x, y + 1))
                if y+1 < 8 and x-1 >= 0 and self.capture(x-1, y+1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x-1, y+1, is_white_turn):
                        self.actual_move.append((x-1, y+1))
                    elif not self.flag:
                        self.valid_move.append((x - 1, y + 1))
                if y+1 < 8 and x+1 <= 7 and self.capture(x+1, y+1, is_white_turn, board_type):
                    if self.flag and self.future_check(coord, x+1, y+1, is_white_turn):
                        self.actual_move.append((x+1, y+1))
                    elif not self.flag:
                        self.valid_move.append((x + 1, y + 1))

    # finds valid rook moves
    def rook_move(self, coord, x, y, is_white_turn, board_type):

        self.rook_helper(coord, x, y, -1, 0, is_white_turn, board_type)
        self.rook_helper(coord, x, y, 1, 0, is_white_turn, board_type)

        self.rook_helper(coord, x, y, 0, -1, is_white_turn, board_type)
        self.rook_helper(coord, x, y, 0, 1, is_white_turn, board_type)

    # rook helper function
    def rook_helper(self, coord, x, y, dx, dy, is_white_turn, board_type):
        for i in itertools.count(start=1):
            new_x = x + dx*i
            new_y = y + dy*i

            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if board_type[new_y][new_x] == "--":
                    if self.flag and self.future_check(coord, new_x, new_y, is_white_turn):
                        self.actual_move.append((new_x, new_y))
                    elif not self.flag:
                        self.valid_move.append((new_x, new_y))
                else:
                    if self.capture(new_x, new_y, is_white_turn, board_type):
                        if self.flag and self.future_check(coord, new_x, new_y, is_white_turn):
                            self.actual_move.append((new_x, new_y))
                            break
                        elif not self.flag:
                            self.valid_move.append((new_x, new_y))
                            break
                    else:
                        break
            else:
                break

    # finds valid knight moves
    def knight_move(self, coord, x, y, is_white_turn, board_type):
        if y < 7 and x > 1 and (board_type[y+1][x-2] == "--" or self.capture(x-2, y+1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x-2, y+1, is_white_turn):
                self.actual_move.append((x-2, y+1))
            elif not self.flag:
                self.valid_move.append((x - 2, y + 1))
        if y > 0 and x > 1 and (board_type[y-1][x-2] == "--" or self.capture(x-2, y-1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x - 2, y - 1, is_white_turn):
                self.actual_move.append((x-2, y-1))
            elif not self.flag:
                self.valid_move.append((x-2, y-1))
        if y < 7 and x < 6 and (board_type[y+1][x+2] == "--" or self.capture(x+2, y+1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x + 2, y + 1, is_white_turn):
                self.actual_move.append((x+2, y+1))
            elif not self.flag:
                self.valid_move.append((x + 2, y + 1))
        if y > 0 and x < 6 and (board_type[y-1][x+2] == "--" or self.capture(x+2, y-1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x + 2, y - 1, is_white_turn):
                self.actual_move.append((x+2, y-1))
            elif not self.flag:
                self.valid_move.append((x + 2, y - 1))
        if y > 1 and x < 7 and (board_type[y-2][x+1] == "--" or self.capture(x+1, y-2, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x + 1, y-2, is_white_turn):
                self.actual_move.append((x+1, y-2))
            elif not self.flag:
                self.valid_move.append((x + 1, y - 2))
        if y > 1 and x > 0 and (board_type[y-2][x-1] == "--" or self.capture(x-1, y-2, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x-1, y-2, is_white_turn):
                self.actual_move.append((x-1, y-2))
            elif not self.flag:
                self.valid_move.append((x-1, y - 2))
        if y < 6 and x > 0 and (board_type[y+2][x-1] == "--" or self.capture(x-1, y+2, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x-1, y+2, is_white_turn):
                self.actual_move.append((x-1, y+2))
            elif not self.flag:
                self.valid_move.append((x - 1, y + 2))
        if y < 6 and x < 7 and (board_type[y+2][x+1] == "--" or self.capture(x+1, y+2, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x+1, y+2, is_white_turn):
                self.actual_move.append((x+1, y+2))
            elif not self.flag:
                self.valid_move.append((x + 1, y + 2))

    # finds valid bishop moves
    def bishop_move(self, coord, x, y, is_white_turn, board_type):

        for dx in (-1, 1):
            for dy in (-1, 1):
                self.bishop_helper(coord, x, y, dx, dy, is_white_turn, board_type)

    # helps to generate bishop moves
    def bishop_helper(self, coord, x, y, dx, dy, is_white_turn, board_type):
        # dx, dy represents direction bishop is traveling in
        for i in itertools.count(start=1):
            new_x = x + dx*i
            new_y = y + dy*i

            if 0 <= new_x < 8 and 0 <= new_y < 8:
                if board_type[new_y][new_x] == "--":
                    if self.flag and self.future_check(coord, new_x, new_y, is_white_turn):
                        self.actual_move.append((new_x, new_y))
                    elif not self.flag:
                        self.valid_move.append((new_x, new_y))
                else:
                    if self.capture(new_x, new_y, is_white_turn, board_type):
                        if self.flag and self.future_check(coord, new_x, new_y, is_white_turn):
                            self.actual_move.append((new_x, new_y))
                            break
                        elif not self.flag:
                            self.valid_move.append((new_x, new_y))
                            break
                    else:
                        break
            else:
                break

    # finds valid queen moves
    def queen_move(self, coord, x, y, is_white_turn, board_type):
        # calls rook and bishop since a queen is a combination of a rook and a bishop
        self.bishop_move(coord, x, y, is_white_turn, board_type)
        self.rook_move(coord, x, y, is_white_turn, board_type)

    # finds valid king moves
    def king_move(self, coord, x, y, is_white_turn, board_type):
        if 0 <= y-1 < 8 and 0 <= x < 8 and (board_type[y-1][x] == "--" or self.capture(x, y-1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x, y-1, is_white_turn):
                self.actual_move.append((x, y-1))
            elif not self.flag:
                self.valid_move.append((x, y - 1))
        if 0 <= y+1 < 8 and 0 <= x < 8 and (board_type[y+1][x] == "--" or self.capture(x, y+1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x, y + 1, is_white_turn):
                self.actual_move.append((x, y+1))
            elif not self.flag:
                self.valid_move.append((x, y + 1))
        if 0 <= y < 8 and 0 <= x-1 < 8 and (board_type[y][x-1] == "--" or self.capture(x-1, y, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x-1, y, is_white_turn):
                self.actual_move.append((x-1, y))
            elif not self.flag:
                self.valid_move.append((x - 1, y))
        if 0 <= y < 8 and 0 <= x+1 < 8 and (board_type[y][x+1] == "--" or self.capture(x+1, y, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x+1, y, is_white_turn):
                self.actual_move.append((x+1, y))
            elif not self.flag:
                self.valid_move.append((x + 1, y))
        if 0 <= y-1 < 8 and 0 <= x+1 < 8 and (board_type[y-1][x+1] == "--" or self.capture(x+1, y-1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x+1, y - 1, is_white_turn):
                self.actual_move.append((x+1, y-1))
            elif not self.flag:
                self.valid_move.append((x + 1, y - 1))
        if 0 <= y-1 < 8 and 0 <= x-1 < 8 and (board_type[y-1][x-1] == "--" or self.capture(x-1, y-1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x-1, y - 1, is_white_turn):
                self.actual_move.append((x-1, y-1))
            elif not self.flag:
                self.valid_move.append((x - 1, y - 1))
        if 0 <= y+1 < 8 and 0 <= x-1 < 8 and (board_type[y+1][x-1] == "--" or self.capture(x-1, y+1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x-1, y + 1, is_white_turn):
                self.actual_move.append((x-1, y+1))
            elif not self.flag:
                self.valid_move.append((x - 1, y + 1))
        if 0 <= y+1 < 8 and 0 <= x+1 < 8 and (board_type[y+1][x+1] == "--" or self.capture(x+1, y+1, is_white_turn, board_type)):
            if self.flag and self.future_check(coord, x+1, y + 1, is_white_turn):
                self.actual_move.append((x+1, y+1))
            elif not self.flag:
                self.valid_move.append((x + 1, y + 1))

    # if white turn allow white to capture black pieces and vice versa
    def capture(self, x, y, player_turn, board_type):
        if player_turn and (board_type[y][x] != "--" and board_type[y][x] not in self.white_pieces):
            return True
        elif player_turn is False and (board_type[y][x] != "--" and board_type[y][x] in self.white_pieces):
            return True
        else:
            return False


    # determines if king will be in check if he castles
    def castle_check(self, coords, is_white_turn, is_left):
        self.flag = False
        self.legal_move_generator(coords, self.board, is_white_turn)

        if is_left:
            if is_white_turn:
                if (2, 7) in self.valid_move or (3, 7) in self.valid_move:
                    return False
                return True
            else:
                if  (2, 0) in self.valid_move or (3, 0) in self.valid_move:
                    return False
                return True
        else: 
            if is_white_turn:
                if (5, 7) in self.valid_move or (6, 7) in self.valid_move:
                    return False
                return True
            else:
                if (5, 0) in self.valid_move or (6, 0) in self.valid_move:
                    return False
                return True 

    # checks if king is in check
    def present_check(self, coords, board_type, is_white_turn):
        self.legal_move_generator(coords, board_type, is_white_turn)

        for i in range(8):
            for j in range(8):
                if is_white_turn:
                    if board_type[i][j] == "wK":
                        if (j, i) in self.valid_move:
                            self.white_check = True
                            self.valid_move = []
                            break
                        else:
                            self.white_check = False
                else:
                    if board_type[i][j] == "bK":
                        if (j, i) in self.valid_move:
                            self.black_check = True
                            self.valid_move = []
                            break
                        else:
                            self.black_check = False

    # checks if future move exposes king to check, including pins
    def future_check(self, coords, x, y, is_white_turn):
        self.flag = False
        self.board_copy[y][x] = self.board_copy[coords[1]][coords[0]]
        self.board_copy[coords[1]][coords[0]] = "--"

        if is_white_turn:
            # generates moves for opposite color to check if king is still in check
            self.present_check(coords, self.board_copy, is_white_turn)
            self.board_copy = deepcopy(self.board)
            if self.white_check:
                self.flag = True
                return False
            self.flag = True
            return True
        else:
            self.present_check(coords, self.board_copy, is_white_turn)
            self.board_copy = deepcopy(self.board)
            if self.black_check:
                self.flag = True
                return False
            self.flag = True
            return True

    # en passant
    def en_passant(self, coords, x, y, white):
        x, y = self.new_coordinates[0], self.new_coordinates[1]
        print("en passant shit", x, y)
        print("and also", self.previous_move)
        if white:
            if self.previous_move == ("bp", 2, False) and self.board[y-1][x] == "--":
                if self.flag and self.future_check(coords, x, y-1, white):
                    self.white_en_passant = True
                    self.actual_move.append((x, y-1))
                elif not self.flag:
                    self.valid_move.append((x, y-1))
            else:
                print("en passant false")
        else:
            if self.previous_move == ("wp", 2, True) and self.board[y+1][x] == "--":
                if self.flag and self.future_check(coords, x, y+1, white):
                    self.black_en_passant = True
                    self.actual_move.append((x, y+1))
                elif not self.flag:
                    self.valid_move.append((x, y+1))
        
    # pawn promotion
    def pawn_promotion(self, x, y, player_turn):
        if player_turn:
            self.board[y][x] = "wQ"
        else:
            self.board[y][x] = "bQ"

    # checks if king can castle
    def castle(self, coord, is_white_turn):
        if is_white_turn:
            if self.left_castle(coord, is_white_turn):
                self.actual_move.append((2, 7))
            if self.right_castle(coord, is_white_turn):
                self.actual_move.append((6, 7))
        else:
            if self.left_castle(coord, is_white_turn):
                self.actual_move.append((2, 0))
            if self.right_castle(coord, is_white_turn):
                self.actual_move.append((6, 0))

    # call this under King moves 
    def left_castle(self, coords, white):
        if white:
            # check if king is currently in check
            self.present_check(coords, self.board, white)
            # check if castling will put king in check
            if not self.castle_check(coords, white, True):
                return False
            if self.white_check:
                return False
            elif self.white_king_moved or self.left_white_rook:
                return False
            elif self.board[7][1] != "--" and self.board[7][2] != "--" and self.board[7][3] != "--":
                return False
            self.white_left_castle_move = True
            return True
        else:
            # check if king is currently in check
            self.present_check(coords, self.board, white)
            # check if castling will put king in check
            if not self.castle_check(coords, white, True):
                return False
            if self.black_check:
                return False
            elif self.black_king_moved or self.left_black_rook:
                return False
            elif self.board[0][1] != "--" and self.board[0][2] != "--" and self.board[0][3] != "--":
                return False
            self.black_left_castle_move = True
            return True

    def right_castle(self, coords, white):
        if white:
            self.present_check(coords, self.board, white)
            if not self.castle_check(coords, white, False):
                return False
            if self.white_check:
                return False
            elif self.white_king_moved or self.right_white_rook:
                return False
            elif self.board[7][5] != "--" and self.board[7][6] != "--":
                return False
            self.white_right_castle_move = True
            return True
        else: 
            self.present_check(coords, self.board, white)
            if not self.castle_check(coords, white, False):
                return False
            if self.black_check:
                return False
            elif self.black_king_moved or self.right_black_rook:
                return False
            elif self.board[0][5] != "--" and self.board[0][6]:
                return False
            self.black_right_castle_move = True
            return True

    # checks if the game is over via checkmate which means a player is in check and has 0 valid moves
    def verify_checkmate(self, white_turn):
        if white_turn: 
            if len(self.actual_move)==0 and self.white_check:
                return True
        else: 
            if len(self.actual_move)==0 and self.black_check:
                return True
        return False

    # checks if game is over via stalemate
    def verify_stalemate(self, white_turn):
        if white_turn:
            if len(self.actual_move)==0 and not self.white_check:
                return True
        else:
            if len(self.actual_move)==0 and not self.black_check:
                return True
        return False

    # generates all legal moves
    def legal_move_generator(self, coords, board_type, is_white_turn):
        for i in range(8):
            for j in range(8):
                if is_white_turn:
                    if board_type[i][j] != "--" and board_type[i][j] not in self.white_pieces:
                        self.move_helper(coords, j, i, not is_white_turn, board_type)
                else:
                    if board_type[i][j] != "--" and board_type[i][j] in self.white_pieces:
                        self.move_helper(coords, j, i, not is_white_turn, board_type)

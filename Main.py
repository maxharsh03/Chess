import pygame as p
import sys
import ChessBoard as chess
p.init()

# dimensions of window
WIDTH = HEIGHT = 512
# numbers of rows and columns of chess board
ROWS = COLUMNS = 8
# size of each square on board
SIZE = WIDTH//ROWS
# game window
WN = p.display.set_mode((WIDTH, HEIGHT))
# set title name
p.display.set_caption("Chess")
# dictionary of pieces
IMAGES = {}
# map of pieces and their current position on the board
PIECE_MAP = {}


def load_pieces():
    # abbreviations of pieces for quick access
    pieces = ['wR', 'wN', 'wB', 'wK', 'wQ', 'wp', 'bR', 'bN', 'bB', 'bK', 'bQ', 'bp']

    # load images into dictionary
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("cburnett/" + piece + ".png"), (SIZE, SIZE))


# draw white and gray squares
def draw_board():
    colors = [(200, 200, 200), (100, 100, 100)]
    for r in range(ROWS):
        for c in range(ROWS):
            p.draw.rect(WN, colors[(r + c) % 2], (r*SIZE, c*SIZE, SIZE, SIZE))


# draw pieces on board
def draw_pieces(b, clicked):
    for r in range(ROWS):
        for c in range(ROWS):
            if b.board[r][c] != "--":
                WN.blit(IMAGES[b.board[r][c]], (c*SIZE, r*SIZE))

# prints board
def print_board(b):
    for i in range(ROWS):
        print(b.board[i])

# highlights squares if they are valid
def square_color():
    pass

# main game loop
def main():
    clock = p.time.Clock()  # clock object
    running = True  # boolean for main game loop
    clicked = False  # tracks whether mouse is clicked
    b = chess.Board()  # loads in chess board
    load_pieces()  # loads pieces on board
    white_turn = True  # tracks whose turn it is
    selected = ()  # position that the player clicked on
    selected_list = []  # list of player clicks

    # main game loop
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN:
                if event.button == 1:
                    location = p.mouse.get_pos()  # gets current mouse pos
                    x = location[0]//64  # converts x coordinate of pos into an integer value 0-7
                    y = location[1]//64  # converts y coordinate of pos into an integer value 0-7
                    if (x, y) == selected:  # undo move when player clicks same piece twice
                        selected = ()
                        selected_list = []
                        b.valid_move = []
                    else:
                        selected = (x, y)
                        selected_list.append(selected)
                        if len(selected_list) == 1:
                            b.move(selected_list[0], white_turn)
                            if b.checkmate:
                                running = False
                            elif b.stalemate:
                                running = False
                            print("Valid moves: ", set(b.valid_move))
                            print("Actual moves:", set(b.actual_move))
                    # if len > 1 we have a valid move that's not a repeat
                    if len(selected_list) > 1:
                        # only make move if move valid, also checks if move aligns with color
                        if white_turn and b.turn(selected_list[0]) and selected_list[1] in set(b.actual_move):
                            b.make_move(selected_list, white_turn)
                            white_turn = not white_turn
                        elif not white_turn and not b.turn(selected_list[0]) and selected_list[1] in set(b.actual_move):
                            b.make_move(selected_list, white_turn)
                            white_turn = not white_turn
                        selected = ()
                        selected_list = []


        draw_board()
        draw_pieces(b, clicked)
        clock.tick(60)
        p.display.flip()


main()

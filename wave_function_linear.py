import random
import bpy
from math import radians
import json


class Piece:
    def __init__(self, name, piece, fittings, rotation):
        x_top, x_bottom, y_top, y_bottom = fittings
        self.name = name
        self.piece = piece
        self.x_top = x_top
        self.x_bottom = x_bottom
        self.y_top = y_top
        self.y_bottom = y_bottom
        self.rotation = rotation


cells = {}

target_road_collection = bpy.data.collections['Generated']
road_modules_collection = bpy.data.collections['Modules']

details = '{\
"grid_width":10,\
"grid_height":10,\
"dimension":6}'

details_dict = json.loads(details)

width = details_dict["grid_width"]
height = details_dict["grid_height"]
dimension = details_dict["dimension"]


straight_road_module = road_modules_collection.children['Straight'].objects
l_turn_road_module = road_modules_collection.children['L-turn'].objects
r_turn_road_module = road_modules_collection.children['R-turn'].objects
cross_road_module = road_modules_collection.children['Plus-joint'].objects
t_road_module = road_modules_collection.children['T-joint'].objects
empty_module = road_modules_collection.children['Empty'].objects
dead_end_module = road_modules_collection.children['Dead-end'].objects

straight_road_piece = Piece('Straight', straight_road_module, (1, 1, 0, 0), 0)
straight_road_90_piece = Piece(
    'Straight', straight_road_module, (0, 0, 1, 1), 90)
l_turn_road_piece = Piece('L-turn', l_turn_road_module, (1, 0, 0, 1), 0)
l_turn_270_road_piece = Piece('L-turn', l_turn_road_module, (0, 1, 0, 1), 270)
r_turn_road_piece = Piece('R-turn', r_turn_road_module, (1, 0, 1, 0), 0)
r_turn_90_road_piece = Piece('R-turn', r_turn_road_module, (0, 1, 1, 0), 90)
cross_road_piece = Piece('Cross-roads', cross_road_module, (1, 1, 1, 1), 0)
t_road_piece = Piece('Cross-roads', t_road_module, (1, 1, 1, 0), 0)
t_road_90_piece = Piece('Cross-roads', t_road_module, (0, 1, 1, 1), 90)
t_road_180_piece = Piece('Cross-roads', t_road_module, (1, 1, 0, 1), 180)
t_road_270_piece = Piece('Cross-roads', t_road_module, (1, 0, 1, 1), 270)
empty = Piece('empty', empty_module, (0, 0, 0, 0), 0)
dead_end_piece = Piece('Straight', dead_end_module, (1, 0, 0, 0), 0)
dead_end_90_piece = Piece('Straight', dead_end_module, (0, 0, 1, 0), 90)
dead_end_180_piece = Piece('Straight', dead_end_module, (0, 1, 0, 0), 180)
dead_end_270_piece = Piece('Straight', dead_end_module, (0, 0, 0, 1), 270)

modular_pieces = [straight_road_piece, empty, l_turn_road_piece, r_turn_road_piece, cross_road_piece, t_road_piece,
                  l_turn_270_road_piece, r_turn_90_road_piece, t_road_90_piece, t_road_180_piece, t_road_270_piece, straight_road_90_piece]


class Cell:
    def __init__(self):
        self.possibilities = modular_pieces
        self.is_filled = False
        self.filled_piece = None


for x_index in range(0, width):
    for y_index in range(0, height):
        cells.update({f'{x_index}-{y_index}': Cell()})


def update_possibilities(position, cells):
    x, y = position
    cell = cells.get(f'{x}-{y}')

    updated_possibilities = []
    piece_cell = cells.get(f'{x+1}-{y}')
    piece = empty if piece_cell == None else piece_cell.filled_piece
    if piece != None:
        for possible_piece in cell.possibilities:
            if possible_piece.x_top == piece.x_bottom:
                print("1, x_top, x_bottom", possible_piece.x_top,
                      piece.x_bottom, possible_piece.name, piece.name)
                updated_possibilities.append(possible_piece)
    if len(updated_possibilities) != 0:
        cell.possibilities = updated_possibilities

    updated_possibilities = []
    piece_cell = cells.get(f'{x-1}-{y}')
    piece = empty if piece_cell == None else piece_cell.filled_piece
    if piece != None:
        for possible_piece in cell.possibilities:
            if possible_piece.x_bottom == piece.x_top:
                print(f"2, {x-1}-{y}, x_bottom, x_top", possible_piece.x_bottom,
                      piece.x_top, possible_piece.name, piece.name)
                updated_possibilities.append(possible_piece)
    if len(updated_possibilities) != 0:
        cell.possibilities = updated_possibilities

    updated_possibilities = []
    piece_cell = cells.get(f'{x}-{y+1}')
    piece = empty if piece_cell == None else piece_cell.filled_piece
    if piece != None:
        for possible_piece in cell.possibilities:
            if possible_piece.y_top == piece.y_bottom:
                print(f"3, {x}-{y+1}, y_top, y_bottom", possible_piece.y_top,
                      piece.y_bottom, possible_piece.name, piece.name)
                updated_possibilities.append(possible_piece)
    if len(updated_possibilities) != 0:
        cell.possibilities = updated_possibilities

    updated_possibilities = []
    piece_cell = cells.get(f'{x}-{y-1}')
    piece = empty if piece_cell == None else piece_cell.filled_piece
    if piece != None:
        for possible_piece in cell.possibilities:
            if possible_piece.y_bottom == piece.y_top:
                print(f"4, {x}-{y-1}, y_bottom, y_top", possible_piece.y_bottom,
                      piece.y_top, possible_piece.name, piece.name)
                updated_possibilities.append(possible_piece)
    if len(updated_possibilities) != 0:
        cell.possibilities = updated_possibilities


def add_piece(position, cells):
    x, y = position
    cell = cells.get(f'{x}-{y}')
    piece = cell.possibilities[random.randint(0, len(cell.possibilities)-1)]
    piece_to_be_spawned = piece.piece[random.randint(0, len(piece.piece)-1)]
    piece_copy = piece_to_be_spawned.copy()
    target_road_collection.objects.link(piece_copy)
    piece_copy.location = (x*dimension, y*dimension, 0)
    piece_copy.rotation_euler = (0, 0, radians(piece.rotation))
    cell.filled_piece = piece


def insert_piece():
    for y_index in range(0, width):
        for x_index in range(0, height):
            update_possibilities((x_index, y_index), cells)
            add_piece((x_index, y_index), cells)


insert_piece()

import random
import bpy
from math import radians


details_dict = {
    "grid_width": 10,
    "grid_height": 10,
    "dimension": 6,
    "source_road_collection_name": "Modules",
    "target_road_collection_name": "Generated",
}

width = details_dict["grid_width"]
height = details_dict["grid_height"]
dimension = details_dict["dimension"]

target_road_collection = bpy.data.collections[details_dict["target_road_collection_name"]]
road_modules_collection = bpy.data.collections[details_dict["source_road_collection_name"]]

default_piece = None


def initialize_grids():
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
    modular_pieces = []

    def get_piece(configuration):
        name = configuration["name"]
        source_pieces = road_modules_collection.children[
            configuration["source_collection_child_name"]].objects
        piece_fittings = (
            configuration["x_top"], configuration["x_bottom"], configuration["y_top"], configuration["y_bottom"])
        piece_rotation = configuration["piece_rotation"]
        return Piece(name, source_pieces, piece_fittings, piece_rotation)

    for child in road_modules_collection.children:
        for key in child.keys():
            if key.startswith("WF"):
                values = child[key]
                piece = get_piece(
                    {"name": key, "source_collection_child_name": child.name, "x_top": values[0], "x_bottom": values[1], "y_top": values[2], "y_bottom": values[3], "piece_rotation": values[4]})
                modular_pieces.append(piece)
                if key.startswith("WF_default"):
                    global default_piece
                    default_piece = piece
    # TODO: Handle error if default piece is None

    class Cell:
        def __init__(self):
            self.possibilities = modular_pieces
            self.is_filled = False
            self.filled_piece = None

    for x_index in range(0, width):
        for y_index in range(0, height):
            cells.update({f'{x_index}-{y_index}': Cell()})

    return cells


def update_possibilities(position, cells):
    x, y = position
    cell = cells.get(f'{x}-{y}')

    updated_possibilities = []
    piece_cell = cells.get(f'{x+1}-{y}')
    piece = default_piece if piece_cell == None else piece_cell.filled_piece
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
    piece = default_piece if piece_cell == None else piece_cell.filled_piece
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
    piece = default_piece if piece_cell == None else piece_cell.filled_piece
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
    piece = default_piece if piece_cell == None else piece_cell.filled_piece
    if piece != None:
        for possible_piece in cell.possibilities:
            if possible_piece.y_bottom == piece.y_top:
                print(f"4, {x}-{y-1}, y_bottom, y_top", possible_piece.y_bottom,
                      piece.y_top, possible_piece.name, piece.name)
                updated_possibilities.append(possible_piece)
    if len(updated_possibilities) != 0:
        cell.possibilities = updated_possibilities

    return cells


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
    return cells


def insert_piece(cells):
    for y_index in range(0, width):
        for x_index in range(0, height):
            cells = update_possibilities((x_index, y_index), cells)
            cells = add_piece((x_index, y_index), cells)


cells = initialize_grids()
insert_piece(cells)

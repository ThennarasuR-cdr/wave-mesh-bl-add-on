import random
import bpy
from math import radians

width = None
height = None
depth = None
dimension = None
target_collection = None
source_modules_collection = None

default_piece = None

negative_z = -100
positive_z = 100
any_value = 555


def initialize_grids():
    class Piece:
        def __init__(self, name, piece, fittings, rotation):
            x_top, x_bottom, y_top, y_bottom, z_top, z_bottom = fittings
            self.name = name
            self.piece = piece
            self.x_top = x_top
            self.x_bottom = x_bottom
            self.y_top = y_top
            self.y_bottom = y_bottom
            self.z_top = z_top
            self.z_bottom = z_bottom
            self.rotation = rotation

    cells = {}
    modular_pieces = []

    def get_piece(configuration):
        name = configuration["name"]
        source_pieces = source_modules_collection.children[
            configuration["source_collection_child_name"]].objects
        piece_fittings = (
            configuration["x_top"], configuration["x_bottom"], configuration["y_top"], configuration["y_bottom"], configuration["z_top"], configuration["z_bottom"])
        piece_rotation = configuration["piece_rotation"]
        return Piece(name, source_pieces, piece_fittings, piece_rotation)

    for child in source_modules_collection.children:
        for key in child.keys():
            if key.startswith("WF"):
                values = child[key]
                piece = get_piece(
                    {"name": key, "source_collection_child_name": child.name, "x_top": values[0], "x_bottom": values[1], "y_top": values[2], "y_bottom": values[3], "z_top": values[4], "z_bottom": values[5], "piece_rotation": values[6]})
                modular_pieces.append(piece)
                if key.startswith("WF_default"):
                    global default_piece
                    default_piece = piece

    class Cell:
        def __init__(self):
            self.possibilities = modular_pieces
            self.is_filled = False
            self.filled_piece = None

    for x_index in range(0, width):
        for y_index in range(0, height):
            for z_index in range(0, depth):
                cells.update({f'{x_index}-{y_index}-{z_index}': Cell()})

    return cells


def update_possibilities(position, cells):
    x, y, z = position
    cell = cells.get(f'{x}-{y}-{z}')

    def update_possibilities_for_neighbor(x_position, y_position, z_position, current_cell, cells, neighbor_position):
        updated_possibilities = []
        piece_cell = cells.get(f'{x_position}-{y_position}-{z_position}')
        piece = default_piece if piece_cell == None else piece_cell.filled_piece
        print("neighbor_position", z_position)

        for possible_piece in current_cell.possibilities:
            if neighbor_position == "1,0" and piece != None and possible_piece.x_top == piece.x_bottom:
                updated_possibilities.append(possible_piece)
            if neighbor_position == "-1,0" and piece != None and possible_piece.x_bottom == piece.x_top:
                updated_possibilities.append(possible_piece)
            if neighbor_position == "0,1" and piece != None and possible_piece.y_top == piece.y_bottom:
                updated_possibilities.append(possible_piece)
            if neighbor_position == "0,-1" and piece != None and possible_piece.y_bottom == piece.y_top:
                updated_possibilities.append(possible_piece)
            if neighbor_position == "+z" and piece != None and possible_piece.z_top == piece.z_bottom:
                updated_possibilities.append(possible_piece)
            if neighbor_position == "-z":
                print("Inside -z")
                if z_position == -1:
                    print("z-1", possible_piece.name,
                          possible_piece.z_bottom)
                    if possible_piece.z_bottom == negative_z:
                        print("Inside z -1", possible_piece.name,
                              possible_piece.z_bottom)
                        updated_possibilities.append(possible_piece)
                else:
                    if possible_piece.z_bottom == piece.z_top:
                        updated_possibilities.append(possible_piece)
        if len(updated_possibilities) != 0:
            current_cell.possibilities = updated_possibilities
        return cells

    cells = update_possibilities_for_neighbor(x+1, y, z, cell, cells, "1,0")
    cells = update_possibilities_for_neighbor(x-1, y, z, cell, cells, "-1,0")
    cells = update_possibilities_for_neighbor(x, y+1, z, cell, cells, "0,1")
    cells = update_possibilities_for_neighbor(x, y-1, z, cell, cells, "0,-1")
    cells = update_possibilities_for_neighbor(x, y, z+1, cell, cells, "+z")
    cells = update_possibilities_for_neighbor(x, y, z-1, cell, cells, "-z")

    return cells


def add_piece(position, cells):
    x, y, z = position
    cell = cells.get(f'{x}-{y}-{z}')
    piece = cell.possibilities[random.randint(0, len(cell.possibilities)-1)]
    piece_to_be_spawned = piece.piece[random.randint(0, len(piece.piece)-1)]
    piece_copy = piece_to_be_spawned.copy()
    target_collection.objects.link(piece_copy)
    piece_copy.location = (x*dimension, y*dimension, z*dimension)
    piece_copy.rotation_euler = (0, 0, radians(piece.rotation))
    cell.filled_piece = piece
    return cells


def insert_piece(cells):
    for x_index in range(0, width):
        for y_index in range(0, height):
            for z_index in range(0, depth):
                cells = update_possibilities(
                    (x_index, y_index, z_index), cells)
                cells = add_piece((x_index, y_index, z_index), cells)


def generate():
    cells = initialize_grids()
    insert_piece(cells)


class ProMeshProperties(bpy.types.PropertyGroup):
    width: bpy.props.IntProperty(name="Width (x)", default=10)
    depth: bpy.props.IntProperty(name="Depth (y)", default=10)
    height: bpy.props.IntProperty(name="height (z)", default=1)
    dimension_of_pieces: bpy.props.IntProperty(
        name="Piece Dimension", default=6)
    target_collection_name: bpy.props.StringProperty(
        name="", default="Generated")
    source_collection_name: bpy.props.StringProperty(
        name="", default="Modules")


class WFMeshGeneratorUI(bpy.types.Panel):
    bl_label = "Procedural Mesh"
    bl_idname = "pro_mesh_ui"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ProMesh"

    def draw(self, context):
        scene = context.scene
        properties = scene.pro_mesh_pointer_prop

        layout = self.layout

        layout.prop(properties, "width")
        layout.prop(properties, "depth")
        layout.prop(properties, "height")
        layout.prop(properties, "dimension_of_pieces")
        layout.label(text="Source Collection name")
        layout.prop(properties, "source_collection_name")
        layout.label(text="Target Collection name")
        layout.prop(properties, "target_collection_name")

        generator_row = layout.row()
        generator_row.operator("mesh.wf_procedural_mesh_generator")


class GenerateRandomMeshWFOperator(bpy.types.Operator):
    bl_idname = "mesh.wf_procedural_mesh_generator"
    bl_label = "Generate"

    def execute(self, context):
        scene = context.scene
        properties = scene.pro_mesh_pointer_prop

        global width, height, depth, dimension, target_collection, source_modules_collection
        width = properties.width
        height = properties.depth
        depth = properties.height
        dimension = properties.dimension_of_pieces
        target_collection = bpy.data.collections[properties.target_collection_name]
        source_modules_collection = bpy.data.collections[properties.source_collection_name]

        generate()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ProMeshProperties)
    bpy.utils.register_class(GenerateRandomMeshWFOperator)
    bpy.utils.register_class(WFMeshGeneratorUI)

    bpy.types.Scene.pro_mesh_pointer_prop = bpy.props.PointerProperty(
        type=ProMeshProperties)


def unregister():
    bpy.utils.unregister_class(ProMeshProperties)
    bpy.utils.unregister_class(GenerateRandomMeshWFOperator)
    bpy.utils.unregister_class(WFMeshGeneratorUI)

    del bpy.types.Scene.pro_mesh_pointer_prop


# TODO: Remove it later
register()

# if __name__ == "__main__":
#    register()

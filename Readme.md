# Mesh generation using simplified 2D wave function collapse

## Introduction
This is an add-on for Blender 3D software that generates mesh using simplified wave function collapse algorithm.

This addon is implemented using Python programming language and can be used on Blender version 3.4.1 or higher.

## Installation
- Download the add-on's zip file from the repository.
- Open Blender and go to Edit -> Preferences -> Add-ons.
- Click on "Install..." and select the downloaded zip file.
- After installation, search for "Mesh Generator" in the add-ons list and activate it.
- The addon is now ready to use.

## Usage
- Open Blender and switch to "3D View" window.
- Press "Shift+A" to open the "Add" menu and select "Mesh".
- From the "Mesh" submenu, select "MeshGen".
- In the "MeshGen" panel that appears, set the desired width, height, dimension and source module collection.
- Press the "Generate" button to generate the mesh.

## Parameters
- Width: The number of cells in the horizontal direction.
- Height: The number of cells in the vertical direction.
- Dimension: The size of each cell.
- Source module name: The name of the collection containing the modular pieces to be used for generating the mesh.
- Target module name: The name of the collection inside which you need the generated mesh.

## How each pieces are connected with each other based on rules?
The pieces are connected using a simplified wave function collapse algorithm. The algorithm determines which pieces are possible to place in a particular cell based on the neighboring pieces. If there is a piece next to a cell, only pieces that fit with the neighboring piece will be considered. Each piece has a set of fittings on each of its sides, and only pieces whose fittings match with the neighboring piece's fittings are considered. If there are multiple pieces that fit the neighboring piece, a random piece is chosen.

## Custom mesh generation
To create custom meshes, 
- Create a source collection, this collection will contain all the different modular pieces.
- Create child collections inside the source collection. Each child collection will contain multiple styles of modular pieces but with same connectivity rule and rotation
- Create custom properties for these child collections with names starting with `WF`.
- The custom property should be a tuple 5 values with connectivity values of x_top, x_bottom, y_top, y_bottom, and rotation of the piece
- After creating the source collection, add the name of the collection to the `Source module collection` of the add on.
- A collection with name `WF_default` is used as the neighbors of the edge pieces.

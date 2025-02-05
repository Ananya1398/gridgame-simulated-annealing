import time
import numpy as np
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=True, render_delay_sec=0.1, gs=8, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board.

# -1 indicates an empty cell
# 0 indicates a cell colored in the first color (indigo by default)
# 1 indicates a cell colored in the second color (taupe by default)
# 2 indicates a cell colored in the third color (veridian by default)
# 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.

# Each shape is represented as a list containing three elements: a) the brush type (number between 0-8),
# b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

# For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

# input()   # <-- workaround to prevent PyGame window from closing after execute() is called, for when GUI set to True. Uncomment to enable.
print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)

####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.

##########################################
# Write all your code in the area below.
##########################################
"""
Additional sources used:
Numpy documentation: https://numpy.org/doc/2.1/reference/random/generated/numpy.random.choice.html
Python documentation: https://docs.python.org/3/library/functions.html#all

Local search algorithm used: Simulated Annealing
"""

import random

def objective_function(grid):
    """
    Here I used the count of empty cells currently in the grid and the number of colors used as
    my Heuristic, the negative of which gave me my objective function.
    """
    empty_cells = np.sum(grid == -1)
    color_count = len(set(grid.flatten()) - {-1})
    return -(empty_cells + color_count)

def get_valid_moves(grid):
    """
    Checking all the empty cells where my agent can place a brush
    """
    return [(x, y) for x in range(grid.shape[1]) for y in range(grid.shape[0]) if grid[y, x] == -1]

def check_valid(grid):
    """
    Reused logic to check validity of current grid from _.checkGrid() function in gridGame.py
    """
    rows, cols = grid.shape

    for i in range(rows):
        for j in range(cols):
            color = grid[i, j]
            if color == -1:
                continue
            if j < cols - 1 and grid[i, j + 1] == color:
                return False
            if i < rows - 1 and grid[i + 1, j] == color:
                return False

    return True

def simulated_annealing(game, T=1000, a=0.9999):
    """
    Main implementation of Simulated Annealing local search algorithm.
    """
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute(
        'export')

    while T > 1 and not done:
        T *= a
        successor_found = False
        current_obj = objective_function(grid)

        while not successor_found:
            available_moves = get_valid_moves(grid)
            if not available_moves:
                return

            # Choosing our next state position from available empty positions
            new_x, new_y = random.choice(available_moves)

            # Choosing our brush shape based on probabilities assigned to brush sizes
            new_shape_options = np.arange(9)
            new_shape_probabilities = [0.02, 0.01, 0.02, 0.2, 0.2, 0.2, 0.2, 0.075, 0.075]
            new_shape = np.random.choice(new_shape_options, p=new_shape_probabilities)

            #Choosing our new state color
            new_color = random.randint(0, len(game.colors) - 1)

            #Moving to our selected shape and color
            shape_diff = (new_shape - game.currentShapeIndex) % len(game.shapes)
            for i in range(shape_diff):
                game.execute('h')

            color_diff = (new_color - game.currentColorIndex) % len(game.colors)
            for i in range(color_diff):
                game.execute('k')

            #Moving to our selected new positions
            horizontal_moves = 'a' if new_x < shapePos[0] else 'd'
            vertical_moves = 'w' if new_y < shapePos[1] else 's'

            for i in range(abs(new_x - shapePos[0])):
                game.execute(horizontal_moves)

            for i in range(abs(new_y - shapePos[1])):
                game.execute(vertical_moves)

            game.execute('p')
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute(
                'export')

            if not check_valid(grid):
                game.execute('undo')
                shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute(
                    'export')
                continue

            new_state = game.execute('export')
            new_grid = new_state[3]
            next_obj = objective_function(new_grid)

            # Deciding whether to accept the new state or not
            if next_obj > current_obj:
                successor_found = True
                current_obj = next_obj
            else:
                delta_E = current_obj - next_obj
                acceptance_prob = np.exp(-delta_E / T)
                if random.uniform(0, 1) < acceptance_prob:
                    successor_found = True
                    current_obj = next_obj
                else:
                    game.execute('undo')

simulated_annealing(game)
print("Final states")
print(game.execute('export'))

########################################

# Do not modify any of the code below.

########################################

end = time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end - start))
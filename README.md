# 2D Kirigami Deployment Simulator

<img src = "https://github.com/lliu12/kirigami_sim/blob/master/media/penrose_expansion.gif" width="400" height="400" /><img src = "https://github.com/lliu12/kirigami_sim/blob/master/media/penrose_hamiltonian.gif" width="400" height="400" /> 

This code simulates the 2D deployment process of a kirigami pattern given its tile geometry and connectivity. The code is written in Python using the 2D rigid body physics library [Pymunk](http://www.pymunk.org).

Any comments and suggestions are welcome. 

If you use this code in your own work, please cite the following paper:

L. Liu, G. P. T. Choi, and L. Mahadevan, "[Quasicrystal kirigami.](https://doi.org/10.1103/PhysRevResearch.4.033114)" Physical Review Research, 4(3), 033114, 2022.

============================================================

A set of deployable quasicrystal patterns (a variety of 5-fold Penrose, 8-fold Ammann-Beenker, 12-fold Stampfli patterns of different sizes) have been included as examples in the info_files folder.

Usage:

Run "run_simulation.py" after setting the desired vertices, constraints, and hull files inside the .py files.

File examples:

Penrose expansion,  5-layer pattern
* vertices_file: _penrose110_vertices.txt_, 
* constraints_file: _penrose110_expansion_constraints.txt_, 
* hull_file: _penrose110_expansion_hull.txt_

Penrose Hamiltonian, 5-layer pattern
* vertices_file: _penrose110_vertices.txt_, 
* constraints_file: _penrose110_hamiltonian_constraints.txt_, 
* hull_file: _penrose110_hamiltonian_hull.txt_

Penrose removal, 5-layer pattern
* vertices_file: _penrose110_nothinrhombs_vertices.txt_, 
* constraints_file: _penrose110_nothinrhombs_constraints1.txt_, 
* hull_file: _penrose110_nothinrhombs_hull1.txt_

============================================================

The simulation runs using data on a pattern's vertices, constraints, and hull. 

The vertices file specifies the coordinates of each tile's vertices. Row i contains the vertex coordinates for tile i and should be formatted (with vertices v in clockwise order) as 

[v1-x-coord | v1-y-coord | v2-x-coord | v2-y-coord | v3-x-coord .... ].

An example showing how tiles were entered for the Penrose pattern is shown below. Tiles are numbered in order, and each tile's Vertex 1 is marked in red.

<img src = "https://github.com/lliu12/kirigami_sim/blob/master/media/vertices_example.png" width="400" height="400" /> 

In the constraints file, order of rows doesn't matter and each row takes the form 

[Tile i | Vertex Number p in Tile i | Tile j | Vertex Number q in Tile j].

A pinjoint is made fixing the distance between vertex p of tile i and vertex q of tile j to be the same distance apart as they are in the contracted pattern state. For example, a row [1 3 2 1] would constrain Tile 1's third vertex and Tile 2's first vertex to be a fixed distance apart. If the two vertices were already in the same position, they will be "connected" and fixed to have the same position. Ideal expansion tiles were produced by constraining two vertices that were at opposite ends of an edge, which fixes the vertices to be one edge-length apart.

The hull file specifies which vertices make up the outer hull of the pattern, in clockwise order. It is needed only for calculating the area and simulating deployment with radial springs pulling outward. Each row takes the form [Tile i | Vertex p] to denote that tile i's pth vertex is a point on the pattern's hull. 

============================================================

Additional notes:
* DISPLAY_SIZE, X_OFFSET, Y_OFFSET, and VERTEX_MULTIPLIER can be used to adjust the scale and view of the expanding pattern; different patterns will be best viewed with different values for these.
* When IS_INTERACTIVE is true, users can click and drag to interact with tiles, right click to pin tiles, press p to save a screenshot of the simulation, press r to reset the simulation, and press v or c to save a file with the current tile vertex/center locations.
* To use the simulation without a hull file, set AUTO_EXPAND and CALCULATE_AREA_PERIM to false.
* Use DISPLAY_EXPANSION_SPRINGS to toggle whether or not to display the springs used for automatic deployment.
* Physical properties like friction, damping, spring strength, and so on can all be set via Pymunk. Pymunk's [documentation](http://www.pymunk.org/en/latest/pymunk.html) is a great resource for this.
* There are compatibility issues between certain versions of Python and Pygame. This may be a reason why the simulation is not working.
* The animations above are produced using data from the simulation, plus additional processing to assign colors, etc.





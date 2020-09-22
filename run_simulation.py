import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util

# define constants

# read in files

# define helper functions

# run game def main: can be in another module I think
    # setting up the bodies, etc
    # make a separate file for event handling tho


# wrapper class that stores space, static pins, tile vertices, tile centers, constraints, pattern_center
# center_bodies, center_shapes, vertex_bodies, vertex_shapes, spring_anchor_coords for auto expand
# bools like is interactive, auto expand, fourier, etc. put these in a params dict?


# constants
# offsets + scaling constant to help get vertices centered in the display screen
X_OFFSET =250
Y_OFFSET = 250
VERTEX_MULTIPLIER = 1
DISPLAY_SIZE = (800,800)
# enable clicking and dragging to interact with tiles
IS_INTERACTIVE = True
# use a given hull file to calculate and display the area of the pattern
CALCULATE_AREA = True
# only display the vertices of shapes (so screenshots can be used for fourier transform)
FOURIER = False
# automatically apply force with this magnitude outwards on pattern
AUTO_EXPAND = True
spring_stiffness = 80
spring_damping = 1000
# mouse event button info
LEFT = 1
RIGHT = 3

# files

# vertices_file = open("info_files/penrose_star1121122_vertices.txt")
# constraints_file = open("info_files/penrose_star1121122_constraints1.txt")

# vertices_file = open("info_files/penrose110_fifth_vertices.txt")
# constraints_file = open("info_files/penrose110_fifth_constraints_dp.txt")

vertices_file = open("info_files/ammannbeenker40_vertices.txt")
constraints_file = open("info_files/ammannbeenker40_constraints2.txt")

# vertices_file = open("info_files/stampfli132_nothinrhombs_vertices.txt")
# constraints_file = open("info_files/stampfli132_nothinrhombs_constraints1.txt")

# vertices_file = open("info_files/grid_unit_vertices.txt")
# constraints_file = open("info_files/grid_unit_constraints.txt")


# vertices_file = open("info_files/stampfli132_vertices.txt")
# constraints_file = open("info_files/stampfli132_constraints2.txt")

if CALCULATE_AREA or AUTO_EXPAND:
    # each row is a hull vertex, where the first num. is tile # and second num. is vertex #
    # hull_file = open("penrose1_hull.txt")
    hull_file = open("info_files/ammannbeenker40_hull2.txt")


# read vertices into tile_vertices
# ith row of vertices file should hold coordinates for the ith tile's vertices, in the form x1 y1 x2 y2 ... 
tile_vertices = []
for l in (vertices_file.read().splitlines()):
    line = l.split()
    tile_vertices.append([(float(line[i-1]) * VERTEX_MULTIPLIER + X_OFFSET, float(line[i]) * VERTEX_MULTIPLIER + Y_OFFSET) 
                          for i in range(len(line)) if i % 2 == 1])

# calculate tile centers by averaging x and y coords of vertices
# return the center of a single tile given a list of its vertices
def get_center(t):
    length = len(t)
    unzipped = list(zip(*t))
    return (sum(unzipped[0])/length, sum(unzipped[1])/length)
tile_centers = [get_center(t) for t in tile_vertices]

# calculate the center of the whole pattern by averaging x and y coords of tile centers
pattern_center = get_center(tile_centers)

# read constraints from txt file into a list where each row has the form:
# [constraint tile 1, vertex number to pin from this tile, constraint tile 2, vertex to pin from this tile]
# subtracts 1 from everything to move to 0-indexing for python
constraints = []
for l in (constraints_file.read().splitlines()):
    line = l.split()
    constraints.append([int(line[0]) - 1,int(line[1]) - 1, int(line[2]) - 1, int(line[3]) - 1])

# close files
vertices_file.close()
constraints_file.close()

# some helper functions
# reset all bodies and constraints to initial state
def reset_bodies(space, static_pins):
    for body in space.bodies:
        body.position = Vec2d(body.start_position)
        body.force = 0,0
        body.torque = 0
        body.velocity = 0,0
        body.angular_velocity = 0
        body.angle = 0
    # for constraint in space.constraints:
    #     if constraint.a == space.static_body or constraint.b == space.static_body:
    #         space.remove(constraint)
    for s in static_pins:
        space.remove(s)
    static_pins.clear()
    color = THECOLORS["lightskyblue1"]
    for shape in space.shapes:
        shape.color = color

# use the shoelace formula to find the area of a polygon, given its vertices in clockwise order
def segments(v):
    return zip(v, v[1:] + [v[0]])

def area(v):
    return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(v)))

if CALCULATE_AREA:
    hull_vertices = []
    for l in (hull_file.read().splitlines()):
        line = l.split()
        hull_vertices.append([int(line[0]) - 1, int(line[1]) - 1])
    hull_file.close()
    initial_hull_area = area([tile_vertices[(v[0])][(v[1])] for v in hull_vertices])

# run game
def main():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY_SIZE, 0) 
    _, height = screen.get_size()
    static_pins = []
    max_scr = 1

    # conversions between pygame and pymunk coordinates
    def to_pygame(p):
        return int(p.x), int(-p.y+height)
    def from_pygame(p): 
        return to_pygame(p)
        
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 16)
    
    # set up space
    space = pm.Space()
    space.damping = .6 # control drag in the space, with 1 being no drag
    reset_bodies(space, static_pins)
    mouse_body = pm.Body(body_type=pm.Body.KINEMATIC)

    # add bodies and shapes to centers of tiles
    center_bodies = []
    center_shapes = []
    for i in range(len(tile_centers)):
        (node_x, node_y) = tile_centers[i]
        mass = 10
        moment = pm.moment_for_poly(mass, tile_vertices[i])
        body = pm.Body(mass, moment)
        body.position = (node_x, node_y)
        body.start_position = Vec2d(body.position)
        shape = pm.Poly(body, list(map(lambda x:  ((x[0] - node_x) * 1, (x[1] - node_y) * 1), tile_vertices[i])))
        shape.elasticity = 0
        space.add(body, shape)
        center_bodies.append(body)
        center_shapes.append(shape)

    # add shapes at vertices that do not generate collisions
    vertex_bodies = []
    vertex_shapes = []
    for i in range(len(tile_vertices)):
        vertex_bodies.append([])
        vertex_shapes.append([])
        for (node_x, node_y) in tile_vertices[i]:
            mass = 1
            radius = 5
            moment = pm.moment_for_circle(mass, 0, radius, (0,0))
            body = pm.Body(mass, moment)
            body.position = (node_x, node_y)
            body.start_position = Vec2d(body.position)
            vertex_bodies[-1].append(body)
            shape = pm.Circle(body, 5)
            shape.sensor = True
            vertex_shapes[-1].append(shape)
            space.add(body, shape)
            pj = pm.PinJoint(center_bodies[i], body, (node_x - tile_centers[i][0], node_y - tile_centers[i][1]), (0,0))
            space.add(pj)

    # add kirigami connection pins to link tiles together as specified in constraints
    for c in constraints:
        a = center_bodies[(c[0])]
        b = center_bodies[(c[2])]
        pin = pm.PinJoint(a, b, (tile_vertices[(c[0])][(c[1])][0] - a.position.x, tile_vertices[(c[0])][(c[1])][1] - a.position.y), (tile_vertices[(c[2])][(c[3])][0] - b.position.x, tile_vertices[(c[2])][(c[3])][1] - b .position.y))
        space.add(pin)

    # if AUTO_EXPAND, add springs pulling hull tiles outward
    spring_circle_radius = 500
    if AUTO_EXPAND:
        # this code adds a spring for every tile center of tiles in the hull
        hull_tiles = list(zip(*(hull_vertices)))[0]
        for t in hull_tiles:
            body = center_bodies[t]
            if body.position != pattern_center:
                spring_anchor_coords = (Vec2d.normalized(body.position - Vec2d(pattern_center)) * spring_circle_radius) + Vec2d(pattern_center) 
                ds = pm.DampedSpring(body, space.static_body, (0,0), spring_anchor_coords, 0, spring_stiffness, spring_damping)
                space.add(ds)
            else:
                print("Auto-Expansion Note: There was a tile center point lying on the pattern center, which the simulation did not attach an expanding spring to.")


        # # this code adds a spring for every hull vertex, but the way things get weighted, sometimes maximum expansion does not occur e.g. with grid unit vertices
        # for (tile_num, vertex_num) in hull_vertices:
        #     # body = center_bodies[tile_num]
        #     body = vertex_bodies[tile_num][vertex_num]
        #     vertex_init_coords = tile_vertices[tile_num][vertex_num]
        #     if body.position != pattern_center:
        #         spring_anchor_coords = (Vec2d.normalized(body.position - Vec2d(pattern_center)) * spring_circle_radius) + Vec2d(pattern_center) 
        #         ds = pm.DampedSpring(body, space.static_body, (0,0), spring_anchor_coords, 0, spring_stiffness, spring_damping)
        #         space.add(ds)
        #     else:
        #         print("Auto-Expansion Note: There was a hull point lying on the pattern center, which the simulation was unable to attach an expanding spring to.")

    reset_bodies(space, static_pins)
    selected = None

    # event responses
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # press p to save a screenshot of the simulation screen
            elif event.type == KEYDOWN and event.key == K_p:
                temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
                print("Saved a screenshot to " + "kirigami_simulation_" + temp_time + ".png")
                pygame.image.save(screen, str("kirigami_simulation_" + temp_time + ".png"))
            
            if event.type == pygame.USEREVENT+1:
                r = random.randint(1,4)
                for body in space.bodies[:]:
                    body.apply_impulse_at_local_point((-6000,0))
            if event.type == pygame.USEREVENT+2:
                max_scr = 0
                reset_bodies(space, static_pins)
                
            # press r to reset the pattern to contracted state
            elif event.type == KEYDOWN and event.key == K_r and IS_INTERACTIVE:
                max_scr = 0
                reset_bodies(space, static_pins)

            # press v to save a file of current vertex locations
            # vertices are saved with the offset/multiplier transformations done earlier for display purposes undone
            elif event.type == KEYDOWN and event.key == K_v and IS_INTERACTIVE:
                temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
                save_vertices_file = open("kirigami_simulation_vertices" + temp_time + ".txt", "x")
                print("Saved file of current vertices to " + "kirigami_simulation_vertices" + temp_time + ".txt")
                current_vertices = []
                for center in center_shapes:
                    vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                            height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                    center.get_vertices())
                    for pos in vertices:
                        save_vertices_file.write(str(round((pos[0] - X_OFFSET) / VERTEX_MULTIPLIER, 3)) + " " + str(round(((pos[1] - Y_OFFSET) / VERTEX_MULTIPLIER), 3)) + " ")
                    save_vertices_file.write("\n")
                save_vertices_file.close()
                
            elif event.type == MOUSEBUTTONDOWN and IS_INTERACTIVE and event.button == LEFT:
                if selected != None:
                    space.remove(selected)
                p = from_pygame(Vec2d(event.pos))
                hit = space.point_query(p, 0, pm.ShapeFilter())
                if len(hit) > 0:
                    shape = hit[-1].shape
                    rest_length = mouse_body.position.get_distance(shape.body.position)
                    ds = pm.DampedSpring(mouse_body, shape.body, (0,0), (0,0), rest_length, 1000, 10)
                    space.add(ds)
                    selected = ds
            
            elif event.type == MOUSEBUTTONDOWN and IS_INTERACTIVE and event.button == RIGHT:
                if selected != None:
                    space.remove(selected)
                p = from_pygame(Vec2d(event.pos))
                hit = space.point_query_nearest(p, 0, pm.ShapeFilter())
                if hit != None:
                    q = hit.shape.body
                    pinned_already = False
                    existing_pin = None
                    for a in static_pins:
                        if a.b == q:
                            pinned_already = True
                            existing_pin = a
                    if pinned_already:
                        static_pins.remove(existing_pin)
                        space.remove(existing_pin)
                    else:
                        pj = pm.PinJoint(space.static_body, q, (q.position.x, q.position.y), (0,0))
                        space.add(pj)
                        static_pins.append(pj)

            elif event.type == MOUSEBUTTONUP and IS_INTERACTIVE:
                if selected != None:
                    space.remove(selected)
                    selected = None

        mpos = pygame.mouse.get_pos()
        p = from_pygame( Vec2d(mpos) )
        mouse_body.position = p
        
        screen.fill(THECOLORS["white"]) # clear the screen

        # # # apply outward force to all bodies
        # # for body in center_bodies:
        # #     body.apply_force_at_local_point(Vec2d.normalized(body.position - Vec2d(pattern_center)) * 3500, (0,0))

        # # apply outward force only to points on the hull after updating pattern center
        # current_tile_centers = [c.position for c in center_bodies]
        # pattern_center = get_center(current_tile_centers)

        # if AUTO_EXPAND:
        #     for (tile_num, vertex_num) in hull_vertices:
        #         body = center_bodies[tile_num]
        #         vertex_init_coords = tile_vertices[tile_num][vertex_num]
        #         force = Vec2d.normalized(body.position - Vec2d(pattern_center)) * magnitude
        #         body.apply_force_at_local_point(force, (vertex_init_coords[0] - body.position.x, vertex_init_coords[1] - body.position.y))

        # draw shapes
        if not FOURIER:
            # pygame.draw.circle(screen, THECOLORS["black"], to_pygame(Vec2d(pattern_center)), 5)

            for c in space.constraints:
                pv1 = c.a.position + (c.anchor_a).rotated(c.a.angle)
                pv2 = c.b.position + (c.anchor_b).rotated(c.b.angle)
                p1 = to_pygame(pv1)
                p2 = to_pygame(pv2)
                pygame.draw.aalines(screen, THECOLORS["lightskyblue1"], False, [p1,p2])

            for i in range(len(center_shapes)):
                center = center_shapes[i]
                (node_x, node_y) = center.body.position
                pygame.draw.polygon(screen, 
                                    center.color, 
                                    list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())))
                pygame.draw.polygon(screen, 
                                    THECOLORS["lightskyblue2"], 
                                    list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())), 1)
                if CALCULATE_AREA:
                    pygame.draw.polygon(screen, 
                                        THECOLORS["lightskyblue3"], 
                                        list(map(lambda x: to_pygame(x),
                                        [vertex_bodies[(v[0])][(v[1])].position for v in hull_vertices])), 1)
                
            for s in static_pins:
               pygame.draw.circle(screen, THECOLORS["royalblue1"], to_pygame(s.b.position), 5)

        if FOURIER:
            for center in center_shapes:
                # pygame.draw.circle(screen, THECOLORS["black"], to_pygame(center.body.position), 5)
                vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                            height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                    center.get_vertices())
                for pos in vertices:
                    pygame.draw.circle(screen, THECOLORS["black"], pos, 1)

        # space.debug_draw(pm.pygame_util.DrawOptions(screen))

        # Update physics
        fps = 25
        iterations = 20
        dt = 1.0/float(fps)/float(iterations)
        for _ in range(iterations): # 10 iterations to get a more stable simulation
            space.step(dt)
        
        # Flip screen
        if IS_INTERACTIVE:
            screen.blit(font.render("fps: " + str(round(clock.get_fps(), 4)), 1, THECOLORS["darkgrey"]), (5,0))
            screen.blit(font.render("Left click and drag to interact", 1, THECOLORS["darkgrey"]), (5,height - 65))
            screen.blit(font.render("Right click to pin/unpin a tile's position", 1, THECOLORS["darkgrey"]), (5,height - 50))
            screen.blit(font.render("Press R to reset", 1, THECOLORS["darkgrey"]), (5,height - 35))
            screen.blit(font.render("Press P to save screen image", 1, THECOLORS["darkgrey"]), (5,height - 20))
        
        if CALCULATE_AREA: 
            current_hull_area = area([vertex_bodies[(v[0])][(v[1])].position for v in hull_vertices])
            current_scr = (round(current_hull_area / initial_hull_area, 4))
            screen.blit(font.render("SCR (Current Area / Contracted Area) : " + str(current_scr), 1, THECOLORS["darkgrey"]), (5,15))
            if current_scr > max_scr:
                max_scr = current_scr
            screen.blit(font.render("Max SCR Observed: " + str(max_scr), 1, THECOLORS["darkgrey"]), (5,30))
            
        pygame.display.flip()
        clock.tick(fps)
        
if __name__ == '__main__':
    sys.exit(main())
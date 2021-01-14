# simulate tile locations

import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util
from event_handler import EventHandler

class Simulation(object):
    def __init__(self, tile_centers, tile_vertices, constraints, pattern_center, params, hull_vertices, screen, damping = .6, iterations = 20, add_rotary_springs = False):
        self.params = params
        self.space = pm.Space()
        self.space.damping = damping
        self.space.iterations = iterations
        self.mouse = pm.Body(body_type=pm.Body.KINEMATIC)
        self.tile_centers = tile_centers
        self.tile_vertices = tile_vertices 
        self.constraints = constraints
        self.hull_vertices = hull_vertices
        self.pattern_center = pattern_center
        self.selected = None
        self.static_pins = []
        self.max_scr = 1
        self.center_bodies = []
        self.center_shapes = []
        self.expansion_springs = []
        self.rotary_springs = []

        self.reset()

        self.handler = EventHandler(self)
        self.screen = screen
        _, self.height = self.screen.get_size()

        # add bodies and shapes to centers of tiles
        for i in range(len(self.tile_centers)):
            (node_x, node_y) = self.tile_centers[i]
            mass = 10
            moment = pm.moment_for_poly(mass, self.tile_vertices[i])
            body = pm.Body(mass, moment)
            body.position = (node_x, node_y)
            body.start_position = Vec2d(body.position)
            shape = pm.Poly(body, list(map(lambda x:  ((x[0] - node_x) * 1, (x[1] - node_y) * 1), self.tile_vertices[i])))
            shape.elasticity = 0
            self.space.add(body, shape)
            self.center_bodies.append(body)
            self.center_shapes.append(shape)


        # add shapes at vertices that do not generate collisions
        self.vertex_bodies = []
        self.vertex_shapes = []
        for i in range(len(self.tile_vertices)):
            self.vertex_bodies.append([])
            self.vertex_shapes.append([])
            for (node_x, node_y) in self.tile_vertices[i]:
                mass = 1
                radius = 5
                moment = pm.moment_for_circle(mass, 0, radius, (0,0))
                body = pm.Body(mass, moment)
                body.position = (node_x, node_y)
                body.start_position = Vec2d(body.position)
                self.vertex_bodies[-1].append(body)
                shape = pm.Circle(body, 5)
                shape.sensor = True
                self.vertex_shapes[-1].append(shape)
                self.space.add(body, shape)
                pj = pm.PinJoint(self.center_bodies[i], body, (node_x - self.tile_centers[i][0], node_y - self.tile_centers[i][1]), (0,0))
                self.space.add(pj)

        # add kirigami connection pins to link tiles together as specified in constraints
        for c in self.constraints:
            a = self.center_bodies[(c[0])]
            b = self.center_bodies[(c[2])]
            pin = pm.PinJoint(a, b, (self.tile_vertices[(c[0])][(c[1])][0] - a.position.x, self.tile_vertices[(c[0])][(c[1])][1] - a.position.y), (tile_vertices[(c[2])][(c[3])][0] - b.position.x, tile_vertices[(c[2])][(c[3])][1] - b .position.y))
            self.space.add(pin)

        
        if self.params['AUTO_EXPAND'] or self.params['CALCULATE_AREA_PERIM']:
            # this code adds a spring for every tile center of tiles in the hull
            self.hull_tiles = list(zip(*(self.hull_vertices)))[0]

    # if AUTO_EXPAND, add springs pulling hull tiles outward
        if self.params['AUTO_EXPAND']:
            spring_circle_radius = 500
            for t in self.hull_tiles:
                body = self.center_bodies[t]
                if body.position != self.pattern_center:
                    self.spring_anchor_coords = (Vec2d.normalized(body.position - Vec2d(self.pattern_center)) * spring_circle_radius) + Vec2d(self.pattern_center) 
                    ds = pm.DampedSpring(body, self.space.static_body, (0,0), self.spring_anchor_coords, 0, self.params['SPRING_STIFFNESS'], self.params['SPRING_DAMPING'])
                    self.space.add(ds)
                    self.expansion_springs.append(ds)
                else:
                    print("Auto-Expansion Note: There was a tile center point lying on the pattern center, which the simulation did not attach an expanding spring to.")
        self.reset()

    def reset(self):
        for body in self.space.bodies:
            body.position = Vec2d(body.start_position)
            body.force = 0,0
            body.torque = 0
            body.velocity = 0,0
            body.angular_velocity = 0
            body.angle = 0
        for s in self.static_pins:
            self.space.remove(s)
        self.static_pins.clear()
        color = THECOLORS["lightskyblue1"]
        for shape in self.space.shapes:
            shape.color = color
        self.max_scr = 1

        # temp_time = str("{date:%Y%m%d_%H%M%S}".format(date=datetime.datetime.now()))
        # save_centers_file = open("kirigami_simulation_centers" + temp_time + ".txt", "x")
        # print("Saved file of current tile centers to " + "kirigami_simulation_centers" + temp_time + ".txt")
        # current_centers = []
        # for center in self.center_shapes:
        #     save_centers_file.write(str(round((center.body.position[0] - self.params["X_OFFSET"]) / self.params["VERTEX_MULTIPLIER"], 3)) + " " + str(round((center.body.position[1] - self.params["Y_OFFSET"]) / self.params["VERTEX_MULTIPLIER"], 3)) + "\n")
        # save_centers_file.close()


    # maybe need to move this to a drawer class that takes simulation and also screen
    def draw_shapes(self):
        if not self.params['FOURIER']:
            for c in self.space.constraints:
                pv1 = c.a.position + (c.anchor_a).rotated(c.a.angle)
                pv2 = c.b.position + (c.anchor_b).rotated(c.b.angle)
                p1 = self.to_pygame(pv1)
                p2 = self.to_pygame(pv2)
                pygame.draw.aalines(self.screen, THECOLORS["lightskyblue1"], False, [p1,p2])

            for i in range(len(self.center_shapes)):
                center = self.center_shapes[i]
                (node_x, node_y) = center.body.position
                pygame.draw.polygon(self.screen, 
                                    center.color, 
                                    list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())))
                pygame.draw.polygon(self.screen, 
                                    THECOLORS["lightskyblue2"], 
                                    list(map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                        self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                center.get_vertices())), 1)
                if self.params["CALCULATE_AREA_PERIM"]:
                    pygame.draw.polygon(self.screen, 
                                        THECOLORS["lightskyblue3"], 
                                        list(map(lambda x: self.to_pygame(x),
                                        [self.vertex_bodies[(v[0])][(v[1])].position for v in self.hull_vertices])), 1)
                
            for s in self.static_pins:
               pygame.draw.circle(self.screen, THECOLORS["royalblue1"], self.to_pygame(s.b.position), 5)

        if self.params['FOURIER']:
            for center in self.center_shapes:
                vertices = map(lambda x: ((x.rotated(center.body.angle) + center.body.position)[0], 
                                                            self.height - (x.rotated(center.body.angle) + center.body.position)[1]),
                                                                    center.get_vertices())
                for pos in vertices:
                    pygame.draw.circle(self.screen, THECOLORS["black"], pos, 1)

    def to_pygame(self, p):
        return int(p.x), int(-p.y+ self.height)

    def from_pygame(self, p): 
        return self.to_pygame(p)

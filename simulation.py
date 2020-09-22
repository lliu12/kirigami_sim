import sys, random, datetime, os, statistics, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import pymunk.pygame_util

class Simulation(object):
    def __init__(self, tile_centers, tile_vertices, constraints, pattern_center, params, hull_vertices = None, damping = .6):
        self.params = params
        self.space = pm.Space()
        self.space.damping = damping
        self.mouse = pm.Body(body_type=pm.Body.KINEMATIC)
        self.tile_centers = tile_centers
        self.tile_vertices = tile_vertices 
        self.constraints = constraints
        self.hull_vertices = hull_vertices
        self.pattern_center = pattern_center
        self.selected = None

        # add bodies and shapes to centers of tiles
        self.center_bodies = []
        self.center_shapes = []
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
        for i in range(len(self.ile_vertices)):
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
                pj = pm.PinJoint(center_bodies[i], body, (node_x - self.tile_centers[i][0], node_y - self.tile_centers[i][1]), (0,0))
                self.space.add(pj)

        # add kirigami connection pins to link tiles together as specified in constraints
        for c in self.constraints:
            a = self.center_bodies[(c[0])]
            b = self.center_bodies[(c[2])]
            pin = pm.PinJoint(a, b, (self.tile_vertices[(c[0])][(c[1])][0] - a.position.x, self.tile_vertices[(c[0])][(c[1])][1] - a.position.y), (tile_vertices[(c[2])][(c[3])][0] - b.position.x, tile_vertices[(c[2])][(c[3])][1] - b .position.y))
            self.space.add(pin)

        
        if self.params['AUTO_EXPAND'] or self.params['CALCULATE_AREA']:
            # this code adds a spring for every tile center of tiles in the hull
            self.hull_tiles = list(zip(*(self.hull_vertices)))[0]

    # if AUTO_EXPAND, add springs pulling hull tiles outward
        if self.params['AUTO_EXPAND']:
            spring_circle_radius = 500
            for t in self.hull_tiles:
                body = self.center_bodies[t]
                if body.position != self.pattern_center:
                    spring_anchor_coords = (Vec2d.normalized(body.position - Vec2d(self.pattern_center)) * spring_circle_radius) + Vec2d(pattern_center) 
                    ds = pm.DampedSpring(body, space.static_body, (0,0), spring_anchor_coords, 0, self.params['spring_stiffness'], self.params['spring_damping'])
                    self.space.add(ds)
                else:
                    print("Auto-Expansion Note: There was a tile center point lying on the pattern center, which the simulation did not attach an expanding spring to.")


    def reset(self):
        for body in self.space.bodies:
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


    def draw_shapes(self):

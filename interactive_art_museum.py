import datetime
import math

import pygame
import sys
from constants import *
from numpy import arange
from math import cos, sin


def get_points_from_rect(rect: pygame.Rect):
    return [rect.topleft, rect.bottomleft, rect.bottomright, rect.topright]


class Shape:
    def __init__(self, center_point):
        self.center_point = center_point

        self.rects = self.get_rects()
        self.horizontal_polygon_points = get_points_from_rect(self.rects[0])
        self.vertical_polygon_points = get_points_from_rect(self.rects[1])

        self.background_rect = None
        self.number_of_rotations = 0

    def rotate(self, theta):
        self.horizontal_polygon_points = list(
            map(lambda point: rotate_point(point, self.center_point, theta), self.horizontal_polygon_points)
        )
        self.vertical_polygon_points = list(
            map(lambda point: rotate_point(point, self.center_point, theta), self.vertical_polygon_points)
        )

    def create_background_rect(self):
        self.background_rect = pygame.Rect(0, 0, SHAPE_SIZE, SHAPE_SIZE)
        self.background_rect.center = self.center_point

    def is_selected(self):
        return self.number_of_rotations > 0

    def is_colliding_with_point(self, point):
        return self.rects[0].collidepoint(point[0], point[1]) or self.rects[1].collidepoint(point[0], point[1])

    def get_rects(self):
        vertical_rect = pygame.Rect(0, 0, SHAPE_SIZE // 3, SHAPE_SIZE)
        vertical_rect.center = self.center_point
        horizontal_rect = pygame.Rect(0, 0, SHAPE_SIZE, SHAPE_SIZE // 3)
        horizontal_rect.center = self.center_point
        return [vertical_rect, horizontal_rect]

    def draw_background_rect(self, screen, color):
        pygame.draw.rect(screen, color, self.background_rect)

    def draw(self, screen, color):
        pygame.draw.polygon(screen, color, self.vertical_polygon_points)
        pygame.draw.polygon(screen, color, self.horizontal_polygon_points)


def rotate_point(point, center_point, theta):
    x, y = point
    center_x, center_y = center_point
    new_x = cos(theta) * (x - center_x) - sin(theta) * (y - center_y) + center_x
    new_y = sin(theta) * (x - center_x) + cos(theta) * (y - center_y) + center_y
    return new_x, new_y


class Game:
    def __init__(self, screen):
        self.foreground_shapes = []
        self.background_shapes = []

        self.selected_shapes = []
        self.foreground_color = FOREGROUND_COLOR
        self.background_color = BACKGROUND_COLOR

        self.init_shapes(screen)

    def init_shapes(self, screen):
        for x, y in zip(arange(SHAPE_SIZE * -4, WIDTH, SHAPE_SIZE * 4), arange(0, -WIDTH, -SHAPE_SIZE / 3 * 4)):
            for x, y in zip(arange(x, x + SHAPE_SIZE * 4, SHAPE_SIZE),
                            arange(y, y + -SHAPE_SIZE * 1.25, -SHAPE_SIZE / 3)):
                for _ in range(HEIGHT // SHAPE_SIZE + 10):  # + some num
                    new_foreground_shape = Shape((int(x), int(y)))
                    new_background_shape = Shape((int(x + SHAPE_SIZE / 3 * 2), int(y + SHAPE_SIZE / 3)))
                    self.foreground_shapes.append(new_foreground_shape)
                    self.background_shapes.append(new_background_shape)
                    new_foreground_shape.draw(screen, self.foreground_color)
                    new_background_shape.draw(screen, self.background_color)

                    x += SHAPE_SIZE / 3
                    y += SHAPE_SIZE

    def select_shape(self, shape):
        self.selected_shapes.append(shape)

    def update_screen(self, screen):
        # screen.fill(self.background_color)
        self.erase_all_selected_shapes(screen)
        self.update_selected_shapes_rotation(screen)
        self.draw_background_rects_and_selected_shapes(screen)
        # self.draw_all_shapes(screen)

    def update_selected_shapes_rotation(self, screen):
        for i, shape in enumerate(self.selected_shapes):
            shape.rotate(math.pi / 2 / FPS)
            shape.number_of_rotations += 1
            if shape.number_of_rotations >= FPS:
                self.deselect_shape(shape, i)
                shape.draw(screen, self.foreground_color)

    def deselect_shape(self, shape, index):
        shape.number_of_rotations = 0
        shape.background_rect = None
        self.selected_shapes.pop(index)

    def draw_all_shapes(self, screen):
        for shape in self.foreground_shapes:
            shape.draw(screen, self.foreground_color)
            print(self.foreground_color)

    def select_shape_from_position(self, position):
        for shape in self.foreground_shapes:
            if shape.is_colliding_with_point(position):
                if shape.is_selected():
                    return
                self.select_shape(shape)
                shape.create_background_rect()
                return
        if self.selected_shapes:
            return
        else:
            self.switch_background_and_foreground()

    def switch_background_and_foreground(self):
        self.foreground_color, self.background_color = self.background_color, self.foreground_color
        self.foreground_shapes, self.background_shapes = self.background_shapes, self.foreground_shapes

    def draw_background_rects_and_selected_shapes(self, screen):
        for shape in self.selected_shapes:
            shape.draw_background_rect(screen, self.background_color)
            shape.draw(screen, self.foreground_color)

    def init_screen(self, screen):
        screen.fill(self.background_color)
        self.draw_all_shapes(screen)

    def erase_all_selected_shapes(self, screen):
        for shape in self.selected_shapes:
            shape.draw(screen, self.background_color)


def pygame_init():
    pygame.display.init()


def main():
    pygame_init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Interactive Art Museum')
    clock = pygame.time.Clock()

    is_mouse_pressed = False
    game = Game(screen)
    # the_chosen_shape: Shape = game.foreground_shapes[167]
    # the_chosen_shape.color = (0, 255, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # elif event.type == pygame.KEYDOWN:
            #     game.selected_shapes.append(the_chosen_shape)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                is_mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                is_mouse_pressed = False

        # update
        # for shape in game.shapes:
        #     shape.rotate(0.01)

        if is_mouse_pressed:
            mouse_position = pygame.mouse.get_pos()
            game.select_shape_from_position(mouse_position)

        # draw
        game.update_screen(screen)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()

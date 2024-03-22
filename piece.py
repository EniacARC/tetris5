import pygame


class Piece():
    def __init__(self, body, color):
        # speed maybe?
        # ------------
        # self.x = x  # the x coordinates of the piece on the board
        # self.y = y  # the y coordinates of the piece on the board

        self.body = body  # a collections of points (x, y) that make up thew piece. the x y are relative to a 9x9 grid
        self.color = color  # what color is the piece in (R,G,B) format

    # calculate the lowest y value for each x and return it in an array
    def skirt(self):
        skirt = {}

        # Iterate through the tuples
        for x, y in self.body:
            if x not in skirt or y < skirt[x]:
                skirt[x] = y

        # Create an array to store the lowest y value for each x
        # result = [skirt.get(x, None) for x in range(max(skirt.keys()) + 1)]
        result = [skirt.get(x) for x in range(max(skirt.keys()) + 1)]

        return skirt

    # piece rotations - {maybe 4 objects that all point to each other}
    def rotate_counter_clockwise(self):
        rotated_body = []
        for x, y in self.body:
            new_x = 2 - y
            new_y = x
            rotated_body.append((new_x, new_y))
        self.body = rotated_body

    def rotate_clockwise(self):
        rotated_body = []
        for x, y in self.body:
            new_x = y
            new_y = 2 - x
            rotated_body.append((new_x, new_y))
        self.body = rotated_body

    # piece movement - maybe speed
    # def move_y(self):
    #    self.y = self.y - 1

    # def move_x(self, direction):
    #    self.x = self.x + direction  # directions = 1 || -1

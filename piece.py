class Piece:
    """
    A class representing a Tetris piece.

    Attributes:
        body (list): A collection of points (x, y) that make up the piece. The x and y coordinates are relative to a 9x9 grid.
        color (tuple): The color of the piece in (R, G, B) format.
    """
    def __init__(self, body, color):
        """
        Initialize a Piece object with a given body and color

        :param body: A collection of points (x, y) that make up the piece.
        :type body: list of tuples
        :param color: The color of the piece in (R, G, B) format.
        :type color: tuple

        :return: None
        """
        self.body = body
        self.color = color

    def skirt(self):
        """
        Calculate the lowest y value for each x and return it in an array, or it's "skirt".

        :return: An array representing the skirt of the piece.
        :rtype: list
        """
        skirt = {}

        # Iterate through the tuples
        for x, y in self.body:
            if x not in skirt or y < skirt[x]:
                skirt[x] = y

        result = [skirt.get(x) for x in range(max(skirt.keys()) + 1)]

        return result

    def calculate_x_edge(self):
        """
        Calculate the minimum and maximum x coordinates of the piece.

        :return: A tuple containing the minimum and maximum x coordinates.
        :rtype: tuple
        """
        min_x = min(point[0] for point in self.body)
        max_x = max(point[0] for point in self.body)
        return min_x, max_x

    def calculate_y_edge(self):
        """
        Calculate the minimum and maximum y coordinates of the piece.

        :return: A tuple containing the minimum and maximum y coordinates.
        :rtype: tuple
        """
        min_y = min(point[1] for point in self.body)
        max_y = max(point[1] for point in self.body)
        return min_y, max_y

    # piece rotations
    def rotate_counter_clockwise(self):
        """
        Rotate the piece counter-clockwise.

        :return: A new Piece object representing the rotated piece.
        :rtype: Piece
        """
        rotated_body = []
        for x, y in self.body:
            new_x = 2 - y
            new_y = x
            rotated_body.append((new_x, new_y))

        return Piece(rotated_body, self.color)

    def rotate_clockwise(self):
        """
        Rotate the piece clockwise.

        :return: A new Piece object representing the rotated piece.
        :rtype: Piece
        """
        rotated_body = []
        for x, y in self.body:
            new_x = y
            new_y = 2 - x
            rotated_body.append((new_x, new_y))
        return Piece(rotated_body, self.color)



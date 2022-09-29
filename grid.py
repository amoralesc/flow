from utils.values import *
import random


class Grid:
    """Represents the grid of a game. It is a rows * size matrix of tuples,
    where each tuple represents a tile color + state (see utils/values.py
    for the available TILE_STATES).

    The grid is more or less the interface that the game interacts with.
    The GUI is supossed to create a grid and then use it to both send new
    moves and print the current state of the grid as a matrix of tiles."""

    def __init__(self, rows: int, cols: int, qpoints: int, points: list = []) -> None:
        """Initialize a grid with the given rows, cols and points. If points
        is not empty, it will be used as the points of the grid

        Args:
            rows (int): number of rows. Must be between 2 and MAX_GRID_N
            cols (int): number of columns. Must be between 2 and MAX_GRID_N
            qpoints (int): quantity of points. Must be between MIN_POINTS and MAX_POINTS
            points (list, optional): 2D list of tuples where:
                - list[i] are the i-th points
                - list[i][0] is (row, col) of the 1st point of i
                - list[i][1] is (row, col) of the 2nd point of i
                Initialized at random if not given.
        """

        assert (
            MIN_POINTS <= qpoints <= MAX_POINTS
        ), f"qpoints must be between {MIN_POINTS} and {MAX_POINTS}"
        assert 2 <= rows <= MAX_GRID_N, f"rows must be between 2 and {MAX_GRID_N}"
        assert 2 <= cols <= MAX_GRID_N, f"cols must be between 2 and {MAX_GRID_N}"

        self.rows = rows
        self.cols = cols
        self.qpoints = qpoints
        self.points = points
        self._points_set = set()
        if self.points == []:
            self._randomize_points()
        else:
            for i in range(self.points):
                for row, col in self.points[i]:
                    self._points_set.add((row, col))

        assert len(self.points) == self.qpoints, f"len(points) must be equal to qpoints"

        # Create grid with states (0, 0, 0)
        # (0, 0, 0) means empty tile
        self.grid = [[(0, 0, 0) for _ in range(cols)] for _ in range(rows)]
        # Set points
        self._initialize_grid()

        self.paths = [[]] * (qpoints + 1)
        self._is_pathing = False
        self._current_path = None

    def __str__(self) -> str:
        return str(self.grid)

    def __getitem__(self, tuple: tuple[int, int]) -> tuple[int, int, int]:
        """Returns the state of the cell at the given position

        Args:
            tuple (tuple[int, int]): position of the cell

        Returns:
            tuple[int, int, int]: state of the cell
        """
        row, col = tuple
        return self.grid[row][col]

    def __setitem__(self, tuple: tuple[int, int], value: tuple[int, int, int]) -> None:
        """Sets the state of the cell at the given position

        Args:
            tuple (tuple[int, int]): position of the cell
            value (tuple[int, int, int]): state to set
        """

        self.grid[tuple[0]][tuple[1]] = value

    def _randomize_point(self) -> tuple[int, int]:
        """Calculates a random point position

        Returns:
            tuple[int, int]: (row, col) of the random point
        """
        return random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)

    def _randomize_points(self) -> None:
        """Randomize points. Only called if points is not given"""

        for i in range(self.qpoints):
            self.points.append([])
            for _ in range(2):  # 2 points per ith-color
                row, col = self._randomize_point()
                while (row, col) in self._points_set:
                    row, col = self._randomize_point()
                self._points_set.add((row, col))
                self.points[i] += [(row, col)]

    def _initialize_grid(self) -> None:
        """Initialize the grid with the points"""

        for i in range(self.qpoints):
            for row, col in self.points[i]:
                # The state of the points is the index of the point
                # representing the color and 0, 0
                self.grid[row][col] = (i + 1, 0, 0)

    def progress(self) -> float:
        """Calculates the progress of the grid. Progress is defined as the number of
        of cells that have a path divided by the total number of cells.

        Returns:
            float: progress of the grid between 0 and 1
        """

        progress = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col][1:] != (0, 0):
                    progress += 1
        return progress / (self.rows * self.cols)

    def _is_valid_cell(self, row: int, col: int) -> bool:
        """Checks if the given cell is valid

        Args:
            row (int): row of the cell
            col (int): column of the cell

        Returns:
            bool: True if the cell is valid, False otherwise
        """

        if row is None or col is None:
            return False
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _position_of(self, point1: tuple[int, int], point2: tuple[int, int]) -> int:
        """Calculates the position of point2 relative to point1. They are expected to
        be adjacent but never the same cell.

        Args:
            point1 (tuple[int, int]): (row, col) of point1
            point2 (tuple[int, int]): (row, col) of point2

        Returns:
            int: position expressed as 1: up of, 2: right of, 3: down of, 4: left of
        """

        row1, col1 = point1
        row2, col2 = point2
        if row1 == row2:
            if col1 < col2:
                return 2
            else:
                return 4
        elif col1 == col2:
            if row1 < row2:
                return 3
            else:
                return 1

    def _are_adjacent(self, point1: tuple[int, int], point2: tuple[int, int]) -> bool:
        """Checks if point1 and point2 are adjacent

        Args:
            point1 (tuple[int, int]): (row, col) of point1
            point2 (tuple[int, int]): (row, col) of point2

        Returns:
            bool: True if point1 and point2 are adjacent, False otherwise
        """

        row1, col1 = point1
        row2, col2 = point2
        return abs(row1 - row2) + abs(col1 - col2) == 1

    def _cell_is_point(self, row: int, col: int) -> bool:
        """Checks if the given cell is a point

        Args:
            row (int): row of the cell
            col (int): column of the cell

        Returns:
            bool: True if the cell is a point, False otherwise
        """

        return self.grid[row][col][0] != 0 and (
            self.grid[row][col][1] == 0 or self.grid[row][col][2] == 0
        )

    def _restart_path_until_size(self, size: int = 0) -> None:
        """Restart the current path until it has the given size

        Args:
            size (int, optional): size of the path. Defaults to 0.
        """

        while len(self.paths[self._current_path]) > size:
            r, c = self.paths[self._current_path].pop()
            # Mark the cells as empty, except the points
            if not self._cell_is_point(r, c):
                self.grid[r][c] = (0, 0, 0)
            else:
                self.grid[r][c] = (self._current_path, 0, 0)

    def _restart_path_until_cell(self, row: int, col: int) -> None:
        """Restart the current path until it reaches the given cell

        Args:
            row (int): row of the cell
            col (int): column of the cell
        """

        while self.paths[self._current_path][-1] != (row, col):
            r, c = self.paths[self._current_path].pop()
            # Mark the cells as empty, except the points
            if not self._cell_is_point(r, c):
                self.grid[r][c] = (0, 0, 0)
            else:
                self.grid[r][c] = (self._current_path, 0, 0)

    def start_path(self, row: int = None, col: int = None) -> None:
        """Starts a path from the given cell:
        - If the cell is empty / isn't valid, it does nothing.
        - If the cell is a point, it starts a path of that color.
        - If the cell is a non-point color, it continues the path
          from the given cell. That is, it restarts the path from the
          point up to the given cell.

        Args:
            row (int, optional): row of the cell where the path is starting.
            Defaults to None.
            col (int, optional): column of the cell where the path is starting.
            Defaults to None.
        """

        if not self._is_valid_cell(row, col):
            return
        if self.grid[row][col] == (0, 0, 0):
            return

        self._is_pathing = True
        self._current_path = self.grid[row][col][0]

        # If there is no path, start a new path
        if self.paths[self._current_path] == []:
            self.paths[self._current_path] = [(row, col)]
        # If it's a point, restart the path
        elif self._cell_is_point(row, col):
            self._restart_path_until_size()
            self.paths[self._current_path] = [(row, col)]
        # Else, continue the path from the given cell
        else:
            # Restart the path until the given cell
            self._restart_path_until_cell(row, col)
            # Update the state of the cell so that it ends the current path
            pos = self._position_of((row, col), self.paths[self._current_path][-2])
            self.grid[row][col] = (self._current_path, pos, 5)

    def end_path(self) -> None:
        """Ends the current path."""

        self._is_pathing = False
        self._current_path = None

    def _move_to_cell(self, row: int, col: int) -> None:
        """Adds the given cell to the current path.

        Args:
            row (int): row of the cell
            col (int): column of the cell
        """

        # Update the state of the previous last cell so that it continues
        # the path to the new cell
        r, c = self.paths[self._current_path][-1]
        last_pos = self.grid[r][c][1]
        new_pos = self._position_of((r, c), (row, col))
        self.grid[r][c] = (self._current_path, last_pos, new_pos)
        # Update the state of the new cell so that it ends the current path
        pos = self._position_of((row, col), (r, c))
        if self._cell_is_point(row, col):
            self.grid[row][col] = (self._current_path, pos, 0)
        else:
            self.grid[row][col] = (self._current_path, pos, 5)
        # Add the new cell to the path
        self.paths[self._current_path] += [(row, col)]

    def move(self, row: int = None, col: int = None) -> None:
        """Moves the current path to the given cell.
        - If the cell is valid and adjacent to the last path cell,
          it adds the cell to the path.
        - Otherwise, it does nothing.

        Args:
            row (int, optional): row of the cell where the path is moving.
            Defaults to None.
            col (int, optional): column of the cell where the path is moving.
            Defaults to None.
        """

        if not self._is_pathing:
            return
        if not self._is_valid_cell(row, col):
            return
        # Can't move to last cell in path
        if self.paths[self._current_path][-1] == (row, col):
            return
        # Can only move to empty cells
        # or second to last cell in path (to backtrack)
        # or the other point
        if (
            self.grid[row][col] != (0, 0, 0)
            and self.paths[self._current_path][-2]
            != (
                row,
                col,
            )
            and not self.grid[row][col] == (self._current_path, 0, 0)
        ):
            return
        if not self._are_adjacent(self.paths[self._current_path][-1], (row, col)):
            return

        # If the cell is the other point, end the path
        if self.grid[row][col] == (self._current_path, 0, 0):
            # Continue the path to the new cell and end it
            self._move_to_cell(row, col)
            self.end_path()
        elif len(self.paths[self._current_path]) > 1:
            # If the cell is the second to last of the current path, backtrack
            if self.paths[self._current_path][-2] == (row, col):
                r, c = self.paths[self._current_path].pop()
                # Mark the last cell as empty in the grid
                self.grid[r][c] = (0, 0, 0)
                # If the new last cell is a point, mark it as no path
                if len(self.paths[self._current_path]) == 1:
                    r, c = self.paths[self._current_path][0]
                    self.grid[r][c] = (self._current_path, 0, 0)
                # Else, mark it as the end of the path
                else:
                    r, c = self.paths[self._current_path][-1]
                    pos = self._position_of((r, c), self.paths[self._current_path][-2])
                    self.grid[r][c] = (self._current_path, pos, 5)
            # Else, add the cell to the path
            else:
                self._move_to_cell(row, col)
        # Else, add the cell to the path
        else:
            self._move_to_cell(row, col)

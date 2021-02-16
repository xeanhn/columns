import pygame
import random
import columns_mechanics


class Game:
    def __init__(self) -> None:
        """
        Initializes all of the Game data such as the rows and colum  ns. In addition, it initializes
        the game state and generates a new field along with the seven jewels and their respective colors.
        """
        self.rows = 13
        self.columns = 6
        self._running = True
        self.game_state = columns_mechanics.GameState(13, 6, "EMPTY", None)
        self.field = self.game_state.create_new_field()
        self.game_window = (360, 780)
        self.jewels = ["S", "T", "V", "W", "X", "Y", "Z"]
        self.colors = {"S": (255, 0, 0),
                       "T": (255, 127, 0),
                       "V": (255, 242, 0),
                       "W": (118, 255, 0),
                       "X": (0, 255, 255),
                       "Y": (0, 4, 255),
                       "Z": (157, 0, 255)}
        pygame.time.set_timer(30, 500)

    def run(self) -> None:
        """
        Runs the entire game loop and causes a new faller to drop after the current faller
        is frozen and matched jewels are checked and cleared.
        """
        pygame.init()
        self._resize_surface(self.game_window)
        clock = pygame.time.Clock()

        while self._running:
            clock.tick(30)
            self._game_loop()
            self._redraw()
            ready_for_faller = False
            checker = True
            for column in self.field:
                for cell in column:
                    if "*" in cell or "[" in cell or "|" in cell:
                        checker = False
            if checker:
                ready_for_faller = True
            if ready_for_faller:
                self._create_faller()
                self.field = self.game_state.drop(self.field, self.column_faller - 1, self.faller)

        pygame.quit()

    def _create_faller(self) -> None:
        """
        Generates a random faller in a random column.
        """
        self.column_faller = random.randint(1, 6)
        self.faller = [random.choice(self.jewels) for number in range(3)]

    def _game_loop(self) -> None:
        """
        Allows the user to handle the current faller by rotating and moving the faller left and right.
        If the faller lands and freezes, the field is checked for matching and clears matched jewels.
        It also checks if the game has ended. The user is also capable of resizing the window.
        """
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self._end_game()
            elif event.type == pygame.VIDEORESIZE:
                self._resize_surface(event.size)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.field = self.game_state.move_left(self.field)
                elif event.key == pygame.K_RIGHT:
                    self.field = self.game_state.move_right(self.field)
                elif event.key == pygame.K_SPACE:
                    self.field = self.game_state.rotate(self.field)

            elif event.type == 30:
                asterisks_present = self.game_state.checking_for_asterisks(self.field)
                self.field = self.game_state.fall(self.field)
                self.field = self.game_state.matching(self.field)
                if asterisks_present:
                    self.field = self.game_state.clear(self.field)
                    self.field = self.game_state.matching(self.field)
                if self.game_state.check_end_game(self.field, self.rows):
                    self._end_game()

    def _redraw(self) -> None:
        """
        Continuously redraws the entire field and applies the selected background color.
        """
        surface = pygame.display.get_surface()
        surface.fill(pygame.Color(223, 217, 226))
        self._draw_grid()
        self._draw_jewels()

        pygame.display.flip()

    def _draw_grid(self) -> None:
        """
        Draws the grid to help with the aesthetic of the game.
        """
        surface = pygame.display.get_surface()
        color = (255, 255, 255)
        for num_rows in range(0, self.rows):
            rectangle = (0, (num_rows / 13 - 0.0175) * pygame.display.Info().current_h,
                         pygame.display.Info().current_w, pygame.display.Info().current_h / 104)

            pygame.draw.rect(surface, color, rectangle)

        for num_columns in range(0, self.columns):
            rectangle = ((num_columns / 6 - 0.045) * pygame.display.Info().current_w * 1.08, 0,
                         pygame.display.Info().current_h / 104, pygame.display.Info().current_h)

            pygame.draw.rect(surface, color, rectangle)

    def _draw_jewels(self) -> None:
        """
        Draws all of the current jewels on the field.
        """
        for column_index, column in enumerate(self.field):
            for cell_index in range(3, len(column)):
                if self.field[column_index][cell_index] != "   ":
                    self._draw_jewel((column_index, cell_index - 3))

    def _draw_jewel(self, jewel_coordinates: (int, int)) -> None:
        """
        Using the coordinates of the jewel, the jewel is drawn and filled with its respective color.
        If the jewel has landed, it is black for an instance; if the jewel has matched, it is a light
        yellow for an instance.
        """
        fractional_x, fractional_y = jewel_coordinates[0] / 6, jewel_coordinates[1] / 13,
        top_left_pixel_x, top_left_pixel_y = self._get_top_left_pixel_values(fractional_x, fractional_y)
        top_left_pixel_x = 1.080 * top_left_pixel_x
        surface = pygame.display.get_surface()
        pixel_width, pixel_height = self._get_pixel_measurements()
        rectangle = (top_left_pixel_x, top_left_pixel_y, pixel_width, pixel_height)

        if self.field[jewel_coordinates[0]][jewel_coordinates[1] + 3].count("|") > 0:
            jewel_color = (0, 0, 0)
        elif self.field[jewel_coordinates[0]][jewel_coordinates[1] + 3].count("*") > 0:
            jewel_color = (252, 255, 198)
        else:
            jewel_color = self.colors[self.field[jewel_coordinates[0]][jewel_coordinates[1] + 3][1]]

        pygame.draw.rect(surface, jewel_color, rectangle)

    def _get_top_left_pixel_values(self, fractional_x: float, fractional_y: float) -> (float, float):
        """
        Acquires the top left pixel coordinates of the specific jewel.
        """
        pixel_x = fractional_x * pygame.display.Info().current_w
        pixel_y = fractional_y * pygame.display.Info().current_h
        return pixel_x, pixel_y

    def _get_pixel_measurements(self) -> (float, float):
        """
        Acquires the pixel size (width and height) of the jewel.
        """
        pixel_width = 0.1 * pygame.display.Info().current_w
        pixel_height = 0.05 * pygame.display.Info().current_h

        return pixel_width, pixel_height

    def _resize_surface(self, size: (int, int)) -> None:
        """
        Allows the user to resize the window.
        """
        pygame.display.set_mode(size, pygame.RESIZABLE)

    def _end_game(self) -> None:
        """
        Ends the game when prompted to do so.
        """
        self._running = False


if __name__ == "__main__":
    Game().run()

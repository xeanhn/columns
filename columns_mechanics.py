import copy


class GameState:
    def __init__(self, rows: int, columns: int, initial_format: str, field_contents: [[str]]) -> None:
        """
        Initializes all of the data such as the inputted rows, columns, format, and field contents.
        This also initializes the field as well as the field before it was edited by a move. It also
        creates lists for all of the possible jewel conditions such as having brackets, bars, or asterisks.
        """
        self.rows = rows
        self.columns = columns
        self.initial_format = initial_format
        self.field_contents = field_contents
        self.field = []
        self.list_possible_jewels_asterisks = [f"*{chr(i)}*" for i in range(83, 91)]
        self._previous_field = []
        self._list_possible_jewels_brackets = [f"[{chr(i)}]" for i in range(83, 91)]
        self._list_possible_jewels_lines = [f"|{chr(i)}|" for i in range(83, 91)]

    def create_new_field(self) -> [[str]]:
        """
        Creates and returns the field based off of the user input of EMPTY or CONTENTS.
        """
        if self.initial_format == "EMPTY":
            game_field = self._create_blank_field(self.rows, self.columns)
        elif self.initial_format == "CONTENTS":
            blank_field = self._create_blank_field(self.rows, self.columns)
            game_field = self._create_contents_field(blank_field, self.field_contents)

        return game_field

    def drop(self, field: [[str]], column_selection: int, faller_list: [str]) -> [[str]]:
        """
        Drops the faller into the selected column and returns the updated board.
        """

        if field[column_selection][3] != "   ":
            for index in range(len(faller_list)):
                if field[column_selection][index] == "   ":
                    field[column_selection][index] = f"[{faller_list[index]}]"
        else:
            for index in range(len(faller_list)):
                if field[column_selection][index + 1] == "   ":
                    field[column_selection][index + 1] = f"[{faller_list[index]}]"

        last_jewel_index = self._find_last_jewel_index(field[column_selection])

        if field[column_selection][last_jewel_index + 1] != "   ":
            self._landed_no_brackets(field)

        self.field = field
        return self.field

    def rotate(self, field: [[str]]) -> [[str]]:
        """
        Rotates the current faller and returns the updated board.
        """
        for column_index, column in enumerate(field):
            if any(cell in column for cell in self._list_possible_jewels_brackets) \
                    or any(cell in column for cell in self._list_possible_jewels_lines):
                jewels_in_column = self._make_jewel_list(column)
                jewels_in_column_rotated = [jewels_in_column[-1]] + jewels_in_column[:-1]

                jewel_index = 0
                for index_cell, cell in enumerate(column):
                    if cell != "   " and cell.count(" ") != 2:
                        field[column_index][index_cell] = jewels_in_column_rotated[jewel_index]
                        jewel_index += 1

        self.field = field
        return self.field

    def move_left(self, field: [[str]]) -> [[str]]:
        """
        Moves the faller to the left if it is possible and returns the updated board.
        """
        for column_index, column in enumerate(field):
            if any(cell in column for cell in self._list_possible_jewels_brackets) \
                    or any(cell in column for cell in self._list_possible_jewels_lines):

                last_jewel_index = self._find_last_jewel_index(column)
                if column_index != 0:
                    for cell_index, cell in enumerate(column):

                        if cell.count(" ") == 0 and field[column_index - 1][last_jewel_index] == "   ":
                            field[column_index - 1][cell_index] = cell
                            field[column_index][cell_index] = "   "
                            try:
                                if field[column_index - 1][last_jewel_index + 1] == "   ":
                                    field[column_index - 1][cell_index] = "[" + cell[1] + "]"

                                else:
                                    field[column_index - 1][cell_index] = "|" + cell[1] + "|"
                            except IndexError:
                                pass

        self.field = field
        return self.field

    def move_right(self, field):
        """
        Moves the faller to the right if it is possible and returns the updated board.
        """
        duplicated_field = copy.deepcopy(field)
        for column_index, column in enumerate(duplicated_field):

            if any(cell in column for cell in self._list_possible_jewels_brackets) \
                    or any(cell in column for cell in self._list_possible_jewels_lines):

                last_jewel_index = self._find_last_jewel_index(column)

                if column_index != field.index(field[-1]) and field[column_index + 1][last_jewel_index] == "   ":
                    for cell_index, cell in enumerate(column):

                        if cell.count(" ") == 0:
                            field[column_index + 1][cell_index] = cell
                            field[column_index][cell_index] = "   "

                            try:
                                if field[column_index + 1][last_jewel_index + 1] == "   ":
                                    field[column_index + 1][cell_index] = "[" + cell[1] + "]"
                                elif field[column_index + 1][last_jewel_index + 1].count(" ") == 2:
                                    field[column_index + 1][cell_index] = "|" + cell[1] + "|"
                            except IndexError:
                                pass

        self.field = field
        return self.field

    def fall(self, field: [[str]]) -> [[str]]:
        """
        Causes the faller to fall one row down. If it lands on another jewel or if it hits the bottom,
        bars will replace the brackets. If the user wants to freeze the jewels, the bars disappear after
        the next input that causes the faller to fall when it has already landed.
        """
        self._previous_field = field[:]
        for column_index, column in enumerate(field):
            if any(cell in column for cell in self._list_possible_jewels_brackets):
                falling_jewels_and_blanks = column[:]
                frozen_jewels = []
                for cell in column:
                    if cell.count(" ") == 2:
                        falling_jewels_and_blanks.remove(cell)
                        frozen_jewels.append(cell)

                field[column_index] = [falling_jewels_and_blanks[-1]] + falling_jewels_and_blanks[:-1] + frozen_jewels
                last_jewel_index = self._find_last_jewel_index(field[column_index])
                if last_jewel_index == self.rows + 2:
                    self._landed_no_brackets(field)

                try:
                    if field[column_index][last_jewel_index + 1] != "   ":
                        self._landed_no_brackets(field)

                except IndexError:
                    pass

        if self._previous_field == field:
            self._freeze(field)

        self.field = field
        return self.field

    def matching(self, field: [[str]]) -> [[str]]:
        """
        Based off the three private functions that check for matching across the entire board,
        this causes every matched jewel to be surrounded by asterisks and returns the updated board.
        """
        all_matches_coordinates = self._horizontal_matching(field) + self._vertical_matching(field) + \
                                  self._diagonal_matching(field)

        all_matches = set(all_matches_coordinates)
        for coordinate_pair in all_matches:
            field[coordinate_pair[0]][coordinate_pair[1]] = f"*{field[coordinate_pair[0]][coordinate_pair[1]][1]}*"

        self.field = field
        return self.field

    def clear(self, field: [[str]]) -> [[str]]:
        """
        Clears the field of any matched jewels, causes the rest of the frozen jewels to
        automatically fall to the bottom, and returns the updated field.
        """
        cleared_matches_field = self._deleting_matches(field)
        fallen_jewels_field = self._automatic_fall(cleared_matches_field)

        self.field = fallen_jewels_field
        return self.field

    def checking_for_asterisks(self, field) -> bool:
        """
        Checks the field for any asterisks. This is used to help trigger the clear function to clear the board.
        If there are no asterisks, then matching has finished, and the board should only have frozen jewels.
        """
        asterisks_present = False
        for column_index, column in enumerate(field):
            if any(cell in column for cell in self.list_possible_jewels_asterisks):
                asterisks_present = True

        return asterisks_present

    def check_end_game(self, end_field: [[str]], rows: int) -> bool:
        """
        Checks if the game is over. If there are no asterisks in any column and if the length of any
        of the columns is greater than the field rows, then it ends the game.
        """
        asterisk_counter = 0
        length_counter = 0

        for column in end_field:
            frozen_jewels = []
            if any(cell in column for cell in self.list_possible_jewels_asterisks):
                asterisk_counter += 1
            for cell in column:
                if cell.count(" ") == 2:
                    frozen_jewels.append(cell)
            if len(frozen_jewels) > rows:
                length_counter += 1
        return asterisk_counter == 0 and length_counter != 0

    def _create_blank_field(self, rows: int, columns: int) -> [[str]]:
        """
        Creates and returns an empty board based on the inputted rows and columns.
        """
        field = []
        for col in range(columns):
            field.append([])
            for row in range(rows + 3):
                field[-1].append("   ")
        self.field = field
        return self.field

    def _create_contents_field(self, field: [[str]], field_contents: [[str]]) -> [[str]]:
        """
        Creates and returns a field with contents based off of the user inputs.
        """
        blank_field_copy = field[:]
        jewel_index = 0
        for column_index, column in enumerate(blank_field_copy):

            for line_of_content in field_contents:
                field[column_index].append(line_of_content[jewel_index])
                field[column_index].pop(0)

            jewel_index += 1

        field = self._automatic_fall(field)
        self.field = field
        return self.field

    def _make_jewel_list(self, column_containing_faller: [str]) -> [str]:
        """
        Returns the list of jewels of the current faller.
        """
        faller_jewels = [cell for cell in column_containing_faller if cell.count(" ") == 0]
        return faller_jewels

    def _find_last_jewel_index(self, faller_column: [str]) -> int:
        """
        Returns the last faller jewel index in its respective column.
        """
        jewels_in_column = self._make_jewel_list(faller_column)
        last_jewel = jewels_in_column[-1]
        last_jewel_index = int((''.join(faller_column).rindex(last_jewel)) / 3)

        return last_jewel_index

    def _landed_no_brackets(self, field: [[str]]) -> [[str]]:
        """
        Changes all of the brackets to bars if the faller has landed and returns the updated board.
        """
        translation = str.maketrans("[]", "||")
        for column_index, column in enumerate(field):
            if any(cell in column for cell in self._list_possible_jewels_brackets):
                for index_cell, cell in enumerate(column):
                    field[column_index][index_cell] = cell.translate(translation)

        self.field = field
        return self.field

    def _freeze(self, field: [[str]]) -> [[str]]:
        """
        Changes the bars to empty spaces if the jewels have been frozen and returns the updated board.
        """
        translation = str.maketrans("|", " ")
        for column_index, column in enumerate(field):
            if any(cell in column for cell in self._list_possible_jewels_lines):
                for index_cell, cell in enumerate(column):
                    field[column_index][index_cell] = field[column_index][index_cell].translate(translation)

        self.field = field
        return self.field

    def _automatic_fall(self, field: [[str]]) -> [[str]]:
        """
        If there are floating jewels after the user has implemented contents onto the board or if
        matched jewels are cleared, all remaining jewels fall to the bottom and the updated board is returned.
        """
        copy_field = field[:]
        for column_index, column in enumerate(copy_field):
            reversed_column = column[::-1]
            column_copy = column[:]
            for cell_index, cell in enumerate(reversed(column_copy)):
                if cell == "   ":
                    reversed_column.remove(cell)
                    reversed_column.append(cell)

            field[column_index] = reversed_column[::-1]

        self.field = field
        return self.field

    def _horizontal_matching(self, field: [[str]]) -> [tuple]:
        """
        Returns the coordinates of every horizontally matched jewel in the field.
        """
        matched_jewels = []
        for column_index, column in enumerate(field):
            for cell_index, cell in enumerate(column):
                if cell.count(" ") == 2:
                    try:
                        if cell == field[column_index + 1][cell_index] == field[column_index + 2][cell_index]:
                            matched_jewels.extend(((column_index, cell_index),
                                                   (column_index + 1, cell_index),
                                                   (column_index + 2, cell_index)))

                    except IndexError:
                        pass

        return matched_jewels

    def _vertical_matching(self, field: [[str]]) -> [tuple]:
        """
        Returns the coordinates of every vertically matched jewel in the field.
        """
        matched_jewels = []
        for column_index, column in enumerate(field):
            for cell_index, cell in enumerate(column):
                if cell.count(" ") == 2:
                    try:
                        if cell == field[column_index][cell_index + 1] == field[column_index][cell_index + 2]:
                            matched_jewels.extend(((column_index, cell_index),
                                                   (column_index, cell_index + 1),
                                                   (column_index, cell_index + 2)))
                    except IndexError:
                        pass

        return matched_jewels

    def _diagonal_matching(self, field: [[str]]) -> [tuple]:
        """
        Returns the coordinates of every diagonally matched jewel in the field.
        """
        matched_jewels = []
        for column_index, column in enumerate(field):
            for cell_index, cell in enumerate(column):
                if cell.count(" ") == 2:

                    try:
                        if cell == field[column_index + 1][cell_index + 1] == field[column_index + 2][cell_index + 2]:
                            matched_jewels.extend(((column_index, cell_index),
                                                   (column_index + 1, cell_index + 1),
                                                   (column_index + 2, cell_index + 2)))
                    except IndexError:
                        pass

                    try:
                        if cell == field[column_index + 1][cell_index - 1] == field[column_index + 2][cell_index - 2]:
                            matched_jewels.extend(((column_index, cell_index),
                                                   (column_index + 1, cell_index - 1),
                                                   (column_index + 2, cell_index - 2)))
                    except IndexError:
                        pass

        return matched_jewels

    def _deleting_matches(self, field: [[str]]) -> [[str]]:
        """
        Deletes all of the matched jewels and returns the updated board.
        """
        field_copy = field[:]
        for column_index, column in enumerate(field_copy):
            for cell_index, cell in enumerate(column):
                if cell.count("*") == 2:
                    field[column_index][cell_index] = "   "

        self.field = field
        return self.field

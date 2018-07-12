import copy
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM, LEFT, X
MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board


class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.initUI()

    def initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(
            self, width=WIDTH, height=HEIGHT,
            highlightthickness=1
        )
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(
            self, text="RESET",
            command=self.clear_answers
        )
        check = Button(
            self, text="validate progress",
            command=self.check_progress
        )

        ans = Button(
            self, text="Solution",
            command=self.get_answer
        )

        win_check = Button(
            self, text="Submit",
            command=self.check_victory
        )

        clear = Button(
            self, text="Clear",
            command=self.clear
        )
        clear_button.pack(side=LEFT)
        check.pack(side=LEFT)
        ans.pack(side=LEFT)
        win_check.pack(side=LEFT)
        clear.pack(side=LEFT)

        self.draw_grid()
        self.draw_puzzle()

        self.canvas.bind("<Button-1>", self.cell_clicked)
        self.canvas.bind("<Key>", self.key_pressed)

    def draw_grid(self):
        for i in xrange(10):
            self.canvas.create_line(
                MARGIN + i * SIDE, MARGIN,
                MARGIN + i * SIDE, HEIGHT - MARGIN,
                fill="blue" if i % 3 == 0 else "gray"
            )

            self.canvas.create_line(
                MARGIN, MARGIN + i * SIDE,
                WIDTH - MARGIN, MARGIN + i * SIDE,
                fill="blue" if i % 3 == 0 else "gray"
            )

    def draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in xrange(9):
            for j in xrange(9):
                answer = self.game.answer[i][j]
                original = self.game.puzzle[i][j]
                
                if answer != 0:
                    self.canvas.create_text(
                        MARGIN + j * SIDE + SIDE / 2,
                        MARGIN + i * SIDE + SIDE / 2,
                        text=answer, tags="numbers",
                        fill="black" if answer == original else "slate gray"
                    )

    def draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            self.canvas.create_rectangle(
                MARGIN + self.col * SIDE + 1,
                MARGIN + self.row * SIDE + 1,
                MARGIN + (self.col + 1) * SIDE - 1,
                MARGIN + (self.row + 1) * SIDE - 1,
                outline="red", tags="cursor"
            )

    def draw_victory(self,status=False):
        self.canvas.create_oval(
            MARGIN + SIDE * 2, MARGIN + SIDE * 2,
            MARGIN + SIDE * 7, MARGIN + SIDE * 7,
            tags="victory", fill="dark orange", outline="orange"
        )
        self.canvas.create_text(
            MARGIN + 4 * SIDE + SIDE / 2,
            MARGIN + 4 * SIDE + SIDE / 2,
            text="You win!" if status else "You Lose", tags="victory",
            fill="white", font=("Arial", 32)
        )

    def draw_progress(self, status=False):
        self.canvas.create_oval(
            MARGIN + SIDE * 2, MARGIN + SIDE * 2,
            MARGIN + SIDE * 7, MARGIN + SIDE * 7,
            tags="progress", fill="dark orange", outline="orange"
        )
        self.canvas.create_text(
            MARGIN + 4 * SIDE + SIDE / 2,
            MARGIN + 4 * SIDE + SIDE / 2,
            text="Valid" if status else "inValid", tags="progress",
            fill="white", font=("Arial", 32)
        )

    def cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if (x > MARGIN and x < WIDTH - MARGIN and
            y > MARGIN and y < HEIGHT - MARGIN):
            self.canvas.focus_set()
            row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[row][col] == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1

        self.draw_cursor()

    def key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.answer[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.draw_puzzle()
            self.draw_cursor()

    def check_victory(self):
        if self.game.check(self.game.answer):
            self.draw_victory(status=True)
        else:
            self.draw_victory()

    def clear_answers(self):
        self.game.set_answer_to_puzzle()
        self.canvas.delete("victory")
        self.canvas.delete("progress")
        self.draw_puzzle()

    def clear(self):
        self.canvas.delete("victory")
        self.canvas.delete("progress")

    def get_answer(self):
        self.canvas.delete("victory")
        self.canvas.delete("progress")
        self.game.set_answer_to_puzzle()
        self.game.set_answer_to_solution()
        self.draw_puzzle()

    def check_progress(self):
        if self.game.check(self.game.answer, progress=True):
            self.draw_progress(status=True)
        else:
            self.draw_progress()


class SudokuGame(object):

    def __init__(self, boards_file):
        self.boards = []
        for line in boards_file:
            line = line.strip()
            self.boards.append([])
            for c in line.strip():
                self.boards[-1].append(int(c))
        self.puzzle = self.boards
        self.set_answer_to_puzzle()

    def set_answer_to_solution(self):
        self.sudokuSolver(self.answer)
        self.game_over = True

    def sudokuSolver(self, board):
        i=0
        j=0
        if self.isFull(board):
            self.answer = copy.deepcopy(board)
            return
        else:
            # find the first vacant spot
            for x in range (0, 9):
                for y in range (0, 9):
                    if board[x][y] == 0:
                        i = x
                        j = y
                        break
                else:
                    continue
                break

            # get all the possibilities for i,j
            possiblities = self.possibleEntries(board, i, j)
            for x in range (1, 10):
                if not possiblities[x] == 0:
                    board[i][j] = possiblities[x]
                    self.sudokuSolver(board)
            # backtrack
            board[i][j] = 0

    def isFull(self, board):
        for x in range(0, 9):
            for y in range (0, 9):
                if board[x][y] == 0:
                    return False
        return True

    def possibleEntries(self, board, i, j):
        possibilityArray = {}

        for x in range (1, 10):
            possibilityArray[x] = 0

        #For horizontal entries
        for y in range (0, 9):
            if not board[i][y] == 0:
                possibilityArray[board[i][y]] = 1

        #For vertical entries
        for x in range (0, 9):
            if not board[x][j] == 0:
                possibilityArray[board[x][j]] = 1

        #For squares of three x three
        k = 0
        l = 0
        if i >= 0 and i <= 2:
            k = 0
        elif i >= 3 and i <= 5:
            k = 3
        else:
            k = 6
        if j >= 0 and j <= 2:
            l = 0
        elif j >= 3 and j <= 5:
            l = 3
        else:
            l = 6
        for x in range (k, k + 3):
            for y in range (l, l + 3):
                if not board[x][y] == 0:
                    possibilityArray[board[x][y]] = 1

        for x in range (1, 10):
            if possibilityArray[x] == 0:
                possibilityArray[x] = x
            else:
                possibilityArray[x] = 0

        return possibilityArray


    def set_answer_to_puzzle(self):
        self.game_over = False
        self.answer = []
        for i in xrange(9):
            self.answer.append([])
            for j in xrange(9):
                self.answer[i].append(self.puzzle[i][j])

    def start(self):
        self.puzzle = self.boards
        self.set_answer_to_puzzle()

    def check(self, board, progress=False):
        map_row = [{} for _ in xrange(9)]
        map_col = [{} for _ in xrange(9)]
        map_cell = [[{} for _ in xrange(3)] for __ in xrange(3)]
        for i in xrange(9):
            for j in xrange(9):
                char = board[i][j]
                if char == 0:
                    if progress:
                        continue
                    else:
                        return False
                if char in map_row[i]:
                    return False
                else:
                    map_row[i][char] = [i, j]
                if char in map_col[j]:
                    return False
                else:
                    map_col[j][char] = [i, j]
                if char in map_cell[i / 3][j / 3]:
                    return False
                else:
                    map_cell[i / 3][j / 3][char] = [i, j]
        return True

if __name__ == '__main__':
    try:
        with open('puzzle.txt', 'r') as boards_file:
            game = SudokuGame(boards_file)
            game.start()
            root = Tk()
            ui = SudokuUI(root, game)
            root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
            root.mainloop()
    except Exception:
        print "Puzzles file is invalid."
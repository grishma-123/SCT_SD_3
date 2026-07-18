import random
import customtkinter as ctk


BG = "#161a30"
CARD = "#1f2444"
FIELD = "#2b3159"
FIELD_ALT = "#333a6b"    
ACCENT = "#3ddad7"
ACCENT_DARK = "#28b8b5"
TEXT = "#f2f4ff"
SUBTEXT = "#9aa1c9"

SUCCESS = "#3ddad7"
ERROR = "#ff6b6b"
WARNING = "#ffd166"

FONT_FAMILY = "Segoe UI"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")



def find_empty_cell(board):
    """Return the (row, col) of the empty cell with fewest legal candidates.
    Picking the most constrained cell first makes backtracking much faster
    than always scanning left-to-right."""
    best = None
    best_count = 10
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                count = sum(1 for n in range(1, 10) if is_valid(board, r, c, n))
                if count < best_count:
                    best_count = count
                    best = (r, c)
                    if best_count == 0:
                        return best  
    return best


def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_r, box_c = (row // 3) * 3, (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board[r][c] == num:
                return False
    return True


def solve_board(board):
    
    cell = find_empty_cell(board)
    if cell is None:
       
        return all(board[r][c] != 0 for r in range(9) for c in range(9))

    row, col = cell
    candidates = [n for n in range(1, 10) if is_valid(board, row, col, n)]
    if not candidates:
        return False

    for num in candidates:
        board[row][col] = num
        if solve_board(board):
            return True
        board[row][col] = 0
    return False


def board_has_conflicts(board):
    
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num == 0:
                continue
            board[r][c] = 0
            valid = is_valid(board, r, c, num)
            board[r][c] = num
            if not valid:
                return True
    return False


def generate_full_solution():
    
    board = [[0] * 9 for _ in range(9)]

    def fill(board):
        cell = find_empty_cell(board)
        if cell is None:
            return True
        row, col = cell
        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if is_valid(board, row, col, num):
                board[row][col] = num
                if fill(board):
                    return True
                board[row][col] = 0
        return False

    fill(board)
    return board


def generate_puzzle(clues=32):
    
    board = generate_full_solution()
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    to_remove = 81 - clues
    for r, c in cells[:to_remove]:
        board[r][c] = 0
    return board



DIFFICULTY_CLUES = {
    "Easy": (40, 46),
    "Medium": (32, 38),
    "Hard": (24, 30),
}


def generate_puzzle_for_difficulty(difficulty):
    low, high = DIFFICULTY_CLUES.get(difficulty, DIFFICULTY_CLUES["Medium"])
    return generate_puzzle(clues=random.randint(low, high))



class SudokuApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sudoku Solver")
        self.geometry("820x680")
        self.minsize(740, 600)
        self.configure(fg_color=BG)

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.given_cells = set()  

        self._build_header()
        self._build_grid()
        self._build_controls()
        self._build_status()

    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            header, text="Sudoku Solver",
            font=(FONT_FAMILY, 26, "bold"), text_color=TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Enter the starting numbers, then press Solve.",
            font=(FONT_FAMILY, 13), text_color=SUBTEXT
        ).pack(anchor="w", pady=(2, 0))

    def _build_grid(self):
        board_area = ctk.CTkFrame(self, fg_color="transparent")
        board_area.pack(padx=24, pady=12, fill="both", expand=True)

       
        outer = ctk.CTkFrame(board_area, fg_color=CARD, corner_radius=16)
        outer.pack(side="left", fill="both", expand=True)

        grid_holder = ctk.CTkFrame(outer, fg_color="transparent")
        grid_holder.pack(padx=18, pady=18, expand=True)

        vcmd = (self.register(self._validate_digit), "%P")

        for box_r in range(3):
            for box_c in range(3):
               
                shade = FIELD if (box_r + box_c) % 2 == 0 else FIELD_ALT
                box = ctk.CTkFrame(grid_holder, fg_color=shade, corner_radius=8)
                box.grid(row=box_r, column=box_c, padx=4, pady=4)

                for r in range(3):
                    for c in range(3):
                        row, col = box_r * 3 + r, box_c * 3 + c
                        entry = ctk.CTkEntry(
                            box, width=34, height=34,
                            corner_radius=5,
                            fg_color=CARD,
                            border_color=ACCENT_DARK,
                            border_width=1,
                            text_color=TEXT,
                            font=(FONT_FAMILY, 15, "bold"),
                            justify="center",
                            validate="key",
                            validatecommand=vcmd,
                        )
                        entry.grid(row=r, column=c, padx=2, pady=2)
                        entry.bind("<KeyRelease>", lambda e, rr=row, cc=col: self._on_key(rr, cc))
                        self.entries[row][col] = entry

        
        side_panel = ctk.CTkFrame(board_area, fg_color=CARD, corner_radius=16, width=140)
        side_panel.pack(side="left", fill="y", padx=(12, 0))
        side_panel.pack_propagate(False)

        ctk.CTkLabel(
            side_panel, text="Difficulty",
            font=(FONT_FAMILY, 14, "bold"), text_color=TEXT
        ).pack(anchor="w", padx=16, pady=(18, 10))

        self.difficulty_buttons = {}
        for name in ("Easy", "Medium", "Hard"):
            btn = ctk.CTkButton(
                side_panel, text=name,
                command=lambda n=name: self.on_difficulty_pick(n),
                fg_color=FIELD, hover_color=FIELD_ALT, text_color=TEXT,
                font=(FONT_FAMILY, 13, "bold"), corner_radius=10, height=38,
            )
            btn.pack(fill="x", padx=16, pady=6)
            self.difficulty_buttons[name] = btn

    def _build_controls(self):
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=24, pady=(4, 8))

        for i in range(3):
            controls.grid_columnconfigure(i, weight=1)

        solve_btn = ctk.CTkButton(
            controls, text="Solve", command=self.on_solve,
            fg_color=ACCENT, hover_color=ACCENT_DARK, text_color=BG,
            font=(FONT_FAMILY, 14, "bold"), corner_radius=10, height=40,
        )
        solve_btn.grid(row=0, column=0, padx=4, sticky="ew")

        random_btn = ctk.CTkButton(
            controls, text="Random Puzzle", command=self.on_random,
            fg_color=FIELD, hover_color=FIELD_ALT, text_color=TEXT,
            font=(FONT_FAMILY, 14), corner_radius=10, height=40,
        )
        random_btn.grid(row=0, column=1, padx=4, sticky="ew")

        clear_btn = ctk.CTkButton(
            controls, text="Clear", command=self.on_clear,
            fg_color="transparent", hover_color=FIELD,
            border_width=1, border_color=SUBTEXT, text_color=SUBTEXT,
            font=(FONT_FAMILY, 14), corner_radius=10, height=40,
        )
        clear_btn.grid(row=0, column=2, padx=4, sticky="ew")

    def _build_status(self):
        self.status_label = ctk.CTkLabel(
            self, text="Ready.", font=(FONT_FAMILY, 13),
            text_color=SUBTEXT
        )
        self.status_label.pack(pady=(0, 18))

 
    def _validate_digit(self, proposed):
      
        return proposed == "" or (len(proposed) == 1 and proposed in "123456789")

    def _on_key(self, row, col):
        
        entry = self.entries[row][col]
        entry.configure(text_color=TEXT)
        self.set_status("Ready.", SUBTEXT)

    def _read_board(self):
        board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                val = self.entries[r][c].get().strip()
                board[r][c] = int(val) if val else 0
        return board

    def _write_board(self, board, solved_cells=None):
        solved_cells = solved_cells or set()
        for r in range(9):
            for c in range(9):
                entry = self.entries[r][c]
                entry.delete(0, "end")
                if board[r][c] != 0:
                    entry.insert(0, str(board[r][c]))
                color = ACCENT if (r, c) in solved_cells else TEXT
                entry.configure(text_color=color)

    def set_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    
    def on_solve(self):
        board = self._read_board()

        if board_has_conflicts(board):
            self.set_status(
                "That puzzle has a conflict — check for repeated numbers "
                "in a row, column, or box.", ERROR
            )
            return

        given = {(r, c) for r in range(9) for c in range(9) if board[r][c] != 0}
        solvable_board = [row[:] for row in board]

        if solve_board(solvable_board):
            solved_cells = {
                (r, c) for r in range(9) for c in range(9)
                if (r, c) not in given
            }
            self._write_board(solvable_board, solved_cells)
            self.set_status("Solved! ✓", SUCCESS)
        else:
            self.set_status("No solution exists for this puzzle.", ERROR)

    def on_clear(self):
        empty_board = [[0] * 9 for _ in range(9)]
        self._write_board(empty_board)
        self._highlight_difficulty(None)
        self.set_status("Grid cleared.", SUBTEXT)

    def on_random(self):
        difficulty = random.choice(["Easy", "Medium", "Hard"])
        self._generate_and_load(difficulty)

    def on_difficulty_pick(self, difficulty):
        self._generate_and_load(difficulty)

    def _generate_and_load(self, difficulty):
        puzzle = generate_puzzle_for_difficulty(difficulty)
        self._write_board(puzzle)
        self._highlight_difficulty(difficulty)
        self.set_status(f"{difficulty} puzzle generated.", SUBTEXT)

    def _highlight_difficulty(self, active_name):
        for name, btn in self.difficulty_buttons.items():
            if name == active_name:
                btn.configure(fg_color=ACCENT_DARK, text_color=BG)
            else:
                btn.configure(fg_color=FIELD, text_color=TEXT)


if __name__ == "__main__":
    app = SudokuApp()
    app.mainloop()
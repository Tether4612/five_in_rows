import tkinter as tk
from tkinter import messagebox


ROWS = 6
COLUMN = 7
CELL_SIZE = 80
RADIUS = 30
WIN_LENGTH = 5

PLAYER1 = '#E53935'
PLAYER2 = '#FDD835'
BACKGROUND_COLOR = '#1565C0'
VOID_COLOR = '#ffffff'

board = []
current_player = 1
game_over = False
cliked = False

root = None#гл окно
canvas = None #холст поля
move_status = None#статус хода

def new_game():
    global board, current_player, game_over, cliked
    board = [[0]* COLUMN for _ in range(ROWS)]
    current_player = 1
    game_over = False
    cliked = False
    move_status.config(text='Ход игрока 1(красный)')
    draw_board()

def draw_board():
    canvas.delete('all')
    for r in range(ROWS):
        for c in range(COLUMN):
            x1 = c * CELL_SIZE + (CELL_SIZE - 2 * RADIUS) / 2
            y1 = r * CELL_SIZE + (CELL_SIZE - 2 * RADIUS) / 2
            x2 = x1 + 2 * RADIUS
            y2 = y1 + 2 * RADIUS
            canvas.create_oval(x1,y1,x2,y2, fill=VOID_COLOR, outline='')
            
    for r in range(ROWS):
        for c in range(COLUMN):
            if board[r][c] != 0:
                draw_price(r,c, board[r][c])

def draw_price(r, c, player):
    color = PLAYER1 if player == 1 else PLAYER2
    x1 = c * CELL_SIZE + (CELL_SIZE - 2 * RADIUS) / 2
    y1 = r * CELL_SIZE + (CELL_SIZE -2 * RADIUS) /2
    x2 = x1 + 2 * RADIUS
    y2 = y1 + 2 * RADIUS
    return canvas.create_oval(x1, y1, x2, y2, fill=color, outline='#000', width=2)

def on_click(event):
    global cliked
    if game_over or cliked:
        return
    col = event.x // CELL_SIZE
    cliked_row = event.y // CELL_SIZE
    if not (0 <= col < COLUMN) or not (0 <= cliked_row < ROWS):
        return
    drop_piece(col, cliked_row)

def drop_piece(col, cliked_row):
    global cliked
    target_row = -1
    for r in range(ROWS -1, -1, -1):
        if board[r][col] == 0:
            target_row = r
            break
    if target_row == -1:
        return
    cliked = True
    board[target_row][col] = current_player
    animate_drop(target_row, cliked_row, col, current_player)

def animate_drop(target_r, start_r, col, player):
    color = PLAYER1 if player == 1 else PLAYER2
    
    start_y = start_r * CELL_SIZE + CELL_SIZE / 2
    end_y = target_r * CELL_SIZE + CELL_SIZE / 2
    x_center = col * CELL_SIZE + CELL_SIZE /2
    
    if start_y > end_y:
        start_y = -CELL_SIZE
    
    piece_id = canvas.create_oval(
        x_center - RADIUS, start_y - RADIUS,
        x_center + RADIUS, start_y + RADIUS,
        fill=color, outline='#000', width=2
    )
    velocity= [0] #начальная скорость падения
    current_y = [start_y]#где фишка находится
    gravity = 2.5 #скорость падения
    
    def update_animation():
        velocity[0] += gravity#для ускорения фишки
        current_y[0] += velocity[0]
        if current_y[0] >= end_y:
            current_y[0] = end_y
            canvas.coords(
                piece_id,
                x_center - RADIUS, current_y[0] - RADIUS,
                x_center + RADIUS, current_y[0] + RADIUS
            )
            after_move(target_r, col)
        else:
            canvas.coords(
                piece_id,
                x_center - RADIUS, current_y[0] - RADIUS,
                x_center + RADIUS, current_y[0] + RADIUS
            )
            root.after(15, update_animation)
    update_animation()
    
def after_move(r, c):
    global game_over, cliked, current_player
    
    line = find_winner_line(r, c)
    if line:
        game_over = True
        animate_win(line)
        return
    if is_draw():
        game_over = True
        cliked = False
        move_status.config(text='Ничья!')
        return
    
    cliked = False
    switch_player()
    
def switch_player():
    global current_player
    current_player = 3 -current_player
    name = '1(красные)' if current_player == 1 else '2(желтые)'
    move_status.config(text=f'Ход игрока {name}')

def is_draw():
    return all(board[0][c] != 0 for c in range(COLUMN))

direction = [(0,1),(1,0),(1,1),(1,-1)]#проверка направлений, вправо-вниз-вправо вниз-влево вниз

def find_winner_line(r, c):
    player = board[r][c]
    for dr, dc in direction:
        cells = [(r, c)]
        rr, cc = r + dr, c + dc
        while 0 <= rr < ROWS and 0 <= cc < COLUMN and board[rr][cc] == player:
            cells.append((rr,cc))
            rr += dr
            cc += dc
        rr,cc = r - dr, c -dc 
        while 0 <= rr < ROWS and 0 <= cc < COLUMN and board[rr][cc] == player:
            cells.insert(0, (rr,cc))
            rr -= dr
            cc-= dc
        if len(cells) >= WIN_LENGTH:
            return cells[:WIN_LENGTH]
    return None


def animate_win(cells):
    r1, c1 = cells[0]
    r2, c2 = cells[-1]
    x1 = c1 * CELL_SIZE + CELL_SIZE / 2
    y1 = r1 * CELL_SIZE + CELL_SIZE / 2
    x2 = c2 * CELL_SIZE + CELL_SIZE / 2
    y2 = r2 * CELL_SIZE + CELL_SIZE / 2
    
    line = canvas.create_line(x1,y1,x1,y1, fill='#000000', width=8, capstyle=tk.ROUND, tags='winline')
    
    total_steps = 30
    step=[0]
    
    def draw_line():
        t = step[0] / total_steps
        xe = x1 + (x2 - x1) * t
        ye = y1 + (y2 - y1) * t
        canvas.coords(line,x1,y1,xe,ye)
        step[0]+=1
        if step[0] <= total_steps:
            root.after(15, draw_line)
        else:
            canvas.coords(line,x1,y1,x2,y2)
            blink_line(line, 6)
        
    draw_line()
    
def blink_line(line, count):
    if count <= 0:
        finish_game()
        return
    current = canvas.itemcget(line, 'fill')
    canvas.itemconfig(line, fill='#ffffff' if current == '#000000' else '#000000')
    root.after(150, lambda: blink_line(line, count - 1))
    
def finish_game():
    name = '1(красные)' if current_player == 1 else '2(желтые)'
    move_status.config(text=f'Победил игрок {name}!')
    messagebox.showinfo('Игра окончена', f'Победил игрок{name}')
        
if __name__ == '__main__':
    root = tk.Tk()
    root.title('5 в ряд')
    root.resizable(False, False)
    
    canvas = tk.Canvas(
        root,
        width=COLUMN * CELL_SIZE,
        height=ROWS * CELL_SIZE,
        bg=BACKGROUND_COLOR,
        highlightthickness=0
    )
    
    canvas.pack(padx=10, pady=10)
    
    move_status = tk.Label(root, text='Ход игрока 1(красные)', font=('Arial', 14))
    move_status.pack(pady=5)
    
    reset_button = tk.Button(root, text='Новая игра', font=('Arial', 12), command=new_game)
    reset_button.pack(pady=5)
    
    new_game()
    
    root.bind('<Button-1>', on_click)
    root.mainloop()
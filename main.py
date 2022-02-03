
import tkinter as tk
from random import shuffle
from collections import deque
from tkinter.messagebox import showinfo, showerror


colors = {
    0: 'white',
    1: '#0000ff',
    2: '#09872b',
    3: '#ffd000',
    4: '#d91ed9',
    5: '#851ed9',
    6: '#d98e1e',
    7: '#d91e78',
    8: '#34d91e'
}


class MyButton(tk.Button):
    '''Class for expanding ability of built-in class Button'''

    def __init__(self, master, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3,
                                       font='Calibri 15 bold', *args, **kwargs)
        self.is_mine = False
        self.number = number
        self.count_mines = 0
        self.is_open = False


class MineSweeper:
    '''Main class game behavior'''

    window = tk.Tk()
    window.wm_title('Сапёр')

    def __init__(self, ROWS=7, COLUMS=7, MINES=7):
        '''Initializing buttons, its attributes and class attributes'''

        self.DIC = {}
        self.buttons = []
        self.IS_GAME_OVER = False
        self.IS_FIRST_CLICK = True
        self.IS_ACTIVE = True
        self.ROWS = ROWS
        self.COLUMNS = COLUMS
        self.MINES = MINES
        self.left_mines = MINES
        self.to_open_cells = ROWS * COLUMS - MINES
        self.clock(i=0)
        tk.Label(self.window, text=f'Мины: {self.left_mines}',
                 font='Calibri 13 bold').grid(row=self.ROWS + 4,
                                              column=1, sticky='w', padx=0, columnspan=self.ROWS)

        for i in range(self.ROWS + 2):
            # Creating initial button list plus perimeter barier elements
            temp = []
            for j in range(self.COLUMNS + 2):
                button = MyButton(self.window)
                button.config(command=lambda button=button: self.click(button))
                button.bind('<Button-3>', self.right_click)
                temp.append(button)
            self.buttons.append(temp)

    def right_click(self, event):
        '''Right mouse click behavior'''
        if not self.IS_GAME_OVER:
            current_button = event.widget
            if current_button['state'] == 'normal':
                current_button['state'] = 'disabled'
                current_button['text'] = '🚩'
                current_button['disabledforeground'] = 'red'
                self.left_mines = self.left_mines - 1
            elif current_button['text'] == '🚩':
                current_button['text'] = ''
                current_button['state'] = 'normal'
                self.left_mines = self.left_mines + 1
            tk.Label(self.window, text=f'Мины: {self.left_mines}',
                     font='Calibri 13 bold').grid(row=self.ROWS + 4,
                                                  column=1, sticky='w', padx=0, columnspan=self.ROWS)

    def click(self, clicked_button: MyButton):
        '''Left mouse click behavior'''
        if self.IS_GAME_OVER:
            return None
        if self.IS_FIRST_CLICK:
            self.place_mines(clicked_button.number)
            self.count_mines_in_cells()
            self.IS_FIRST_CLICK = False
        if clicked_button.is_mine:
            clicked_button.config(text='*', background='red',
                                  disabledforeground='black')
            clicked_button.is_open = True
            self.IS_GAME_OVER = True
            showinfo('Game Over', 'Вы проиграли!')
            for i in range(1, self.ROWS + 1):
                for j in range(1, self.COLUMNS + 1):
                    button = self.buttons[i][j]
                    if button.is_mine:
                        button['text'] = '*'
        else:
            if clicked_button['state'] == 'disabled':
                return None
            elif clicked_button.count_mines:
                color = colors.get(clicked_button.count_mines, 'black')
                clicked_button.config(
                    text=clicked_button.count_mines, disabledforeground=color)
                clicked_button.is_open = True
                self.to_open_cells = self.to_open_cells - 1
            else:
                self.breadth_first_search(clicked_button)
        clicked_button.config(state='disable')
        clicked_button.config(relief=tk.SUNKEN)
        if self.to_open_cells == 0:
            self.IS_GAME_OVER = True
            showinfo('Победа!', 'Вы выиграли!')

    def breadth_first_search(self, button):
        '''Searching and opening string of empty buttons'''
        search_queue = deque()
        search_queue += self.DIC[button]
        searched = []
        while search_queue:
            current_button = search_queue.popleft()
            if current_button.count_mines and not current_button.is_open:
                self.click(current_button)
            elif not current_button in searched and not current_button.is_open:
                if current_button['state'] != 'disabled':
                    color = colors.get(current_button.count_mines, 'black')
                    current_button.config(text='', disabledforeground=color)
                    current_button.config(state='disable')
                    current_button.config(relief=tk.SUNKEN)
                    self.to_open_cells = self.to_open_cells - 1
                    current_button.is_open = True
                search_queue += self.DIC[current_button]
                searched.append(current_button)

    def restart(self, ROWS=7, COLUMNS=7, MINES=7):
        '''Restarts the game'''
        try:
            ROWS, COLUMNS, MINES = map(int, (ROWS, COLUMNS, MINES))
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильное значение!')
            return
        self.IS_ACTIVE = False
        [child.destroy() for child in self.window.winfo_children()]
        game = MineSweeper(ROWS=ROWS, COLUMS=COLUMNS, MINES=MINES)
        game.start()

    def create_settings_window(self):
        '''Creates settings window from a dropout menu'''
        window_settings = tk.Toplevel(self.window)
        window_settings.wm_title('Настройки')
        tk.Label(window_settings, text='Количество строк').grid(
            row=0, column=0, sticky='w', padx=10)
        row_entry = tk.Entry(window_settings)
        row_entry.insert(0, self.ROWS)
        row_entry.grid(row=0, column=1, padx=20, pady=20)
        column_entry = tk.Entry(window_settings)
        column_entry.insert(0, self.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)
        tk.Label(window_settings, text='Количество колонок').grid(
            row=1, column=0, sticky='w', padx=10)
        mines_entry = tk.Entry(window_settings)
        mines_entry.insert(0, self.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        tk.Label(window_settings, text='Количество мин').grid(
            row=2, column=0, sticky='w', padx=10)
        save_settings = tk.Button(window_settings, text='Применить',
                                  command=lambda: self.restart(*(
                                      row_entry.get(), column_entry.get(), mines_entry.get())))
        save_settings.grid(row=3, column=0, columnspan=2, pady=20)

    def clock(self, i):
        '''Creating clock for following the time in sec during the game'''
        if not self.IS_GAME_OVER and self.IS_ACTIVE:
            tk.Label(self.window, text=f'Время: {i}',
                     font='Calibri 13 bold').grid(row=self.ROWS + 1,
                                                  column=1, sticky='w', padx=0, columnspan=self.ROWS)
            i += 1
            self.window.after(1000, lambda: self.clock(i))

    def create_widgets(self):
        '''Placing buttons on the window and creating dropout menu'''
        # creating dropout menu
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        setting_menu = tk.Menu(menubar, tearoff=0)
        setting_menu.add_command(label='Играть', command=self.restart)
        setting_menu.add_command(
            label='Настройки', command=self.create_settings_window)
        setting_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Файл', menu=setting_menu)
        # placing buttons on the window and assigning the number to buttons
        counter = 1
        for i in range(1, self.ROWS + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
            for j in range(1, self.COLUMNS + 1):
                tk.Grid.columnconfigure(self.window, i, weight=1)
                button = self.buttons[i][j]
                button.grid(row=i, column=j, stick='NWES')
                button.number = counter
                counter += 1

    def start(self):
        '''Starting the game'''
        self.create_widgets()
        self.window.mainloop()

    def get_mines_buttons(self, number):
        '''Getting mines numbers'''
        mines_list = list(range(1, self.COLUMNS * self.ROWS + 1))
        mines_list.remove(number)
        shuffle(mines_list)
        return mines_list[:self.MINES]

    def place_mines(self, number):
        '''Assigning which button is mine'''
        mines_buttons = self.get_mines_buttons(number)
        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                button = self.buttons[i][j]
                if button.number in mines_buttons:
                    button.is_mine = True

    def count_mines_in_cells(self):
        '''Counting mines in neighboring cells and create a dictionary with neighbours'''
        for i in range(1, self.ROWS + 1):
            for j in range(1, self.COLUMNS + 1):
                button = self.buttons[i][j]
                count_mines = 0
                temp = []
                if not button.is_mine:
                    for row_dx in (-1, 0, 1):
                        for column_dx in (-1, 0, 1):
                            neighbour = self.buttons[i + row_dx][j + column_dx]
                            if neighbour.is_mine:
                                count_mines += 1
                            if neighbour.number != 0:
                                temp.append(neighbour)
                button.count_mines = count_mines
                if temp:
                    self.DIC[self.buttons[i][j]] = temp


if __name__ == '__main__':
    # Creating an object and starting the game
    game = MineSweeper()
    game.start()

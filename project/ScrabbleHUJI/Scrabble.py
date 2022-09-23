import tkinter as tk
from string import ascii_uppercase
from tkinter import messagebox
import webbrowser
import sys

from board import *


class ScrabbleApp:
    APP_TITLE = 'S C R A B B L E'
    WINDOW_SIZE = '1150x750'

    BOARD = ['@', '.', '.', '%', '.', '.', '.', '@', '.', '.', '.', '%', '.', '.', '@',
             '.', '#', '.', '.', '.', '$', '.', '.', '.', '$', '.', '.', '.', '#', '.',
             '.', '.', '#', '.', '.', '.', '%', '.', '%', '.', '.', '.', '#', '.', '.',
             '%', '.', '.', '#', '.', '.', '.', '%', '.', '.', '.', '#', '.', '.', '%',
             '.', '.', '.', '.', '#', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.',
             '.', '$', '.', '.', '.', '$', '.', '.', '.', '$', '.', '.', '.', '$', '.',
             '.', '.', '%', '.', '.', '.', '%', '.', '%', '.', '.', '.', '%', '.', '.',
             '@', '.', '.', '%', '.', '.', '.', '*', '.', '.', '.', '%', '.', '.', '@',
             '.', '.', '%', '.', '.', '.', '%', '.', '%', '.', '.', '.', '%', '.', '.',
             '.', '$', '.', '.', '.', '$', '.', '.', '.', '$', '.', '.', '.', '$', '.',
             '.', '.', '.', '.', '#', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.',
             '%', '.', '.', '#', '.', '.', '.', '%', '.', '.', '.', '#', '.', '.', '%',
             '.', '.', '#', '.', '.', '.', '%', '.', '%', '.', '.', '.', '#', '.', '.',
             '.', '#', '.', '.', '.', '$', '.', '.', '.', '$', '.', '.', '.', '#', '.',
             '@', '.', '.', '%', '.', '.', '.', '@', '.', '.', '.', '%', '.', '.', '@']

    # IMAGES AND TXT FILES:
    HOME_IMAGE = './images/home.png'
    EXIT_IMAGE = './images/quit.png'
    PDF_IMAGE = './images/pdf.png'
    VIDEO_IMAGE = './images/video.png'
    HTML_IMAGE = './images/html.png'
    ABOUT_IMAGE = './images/about.png'
    TITLE_IMAGE = './images/title.png'
    SUBTITLE_IMAGE = './images/subtitle.png'
    LOGO_IMAGE = './images/scrabble_logo_main.png'
    VER_LOGO_IMAGE = './images/ver_scrabble.png'
    STAR_IMAGE = './images/star.png'
    PLAY_IMAGE = './images/start_button.png'
    MALE_IMAGE = './images/male.png'
    FEMALE_IMAGE = './images/female.png'

    # BACKGROUND AND FONT COLORS:
    STANDARD_BG = 'sandy brown'
    SUB_BG = 'dark orange'
    SUB_IN_BG = "old lace"
    SCORE_TIME_FG = "navy"
    RAISED_CUBE_BG = 'cornsilk3'
    GROOVE_CUBE_BG = 'PaleGreen1'
    CUBES_BOARD_BG = 'black'
    FOUND_WORDS_BG = 'wheat2'
    NEIGHBOURS_COLORS = 'light sky blue'
    TW = 'orange red'
    DW = 'maroon1'
    STAR = 'maroon1'
    TL = 'blue2'
    DL = 'deep sky blue'

    BONUS_TILES = {'@': (TW, 'Triple\nWord\nScore'), '#': (DW, 'Double\nWord\nScore'),
                   '$': (TL, 'Triple\nLetter\nScore'), '%': (DL, 'Double\nLetter\nScore'),
                   '*': (STAR, '*')}

    # FONTS:
    FONT_1 = ("default", 25, "bold")
    FONT_2 = ("default", 15, "bold")
    FONT_3 = ("default", 20, "bold")
    FONT_4 = ('times', 10, "bold")
    FONT_5 = ('times', 25, 'bold')
    FONT_6 = ('comic sans ms', 25, "bold")
    FONT_7 = ("default", 22)

    # TEXTS:
    EXIT_TITLE = ' EXIT GAME '
    EXIT_MESSAGE = '\n Are you sure? '.center(40)

    ###################
    ##  CONSTRUCTOR  ##
    ###################

    def __init__(self, root):
        # self._score = 0
        self._root = root
        self._set_root_config()
        self._tiles_imgs = dict()
        self._setup_tiles_images()
        self._create_wrapping_frame()
        self._game_frames = {}
        self._current_frame = None
        self._current_player = None
        self._playing = False
        self._game_over = False
        self._board = None
        # self._create_game_frames()

        self._creat_main_screen()

    # -- END of constructor -- #

    ################################
    ##  GENERAL METHODS & SETUPS  ##
    ################################

    def _set_root_config(self):
        self._root.title(ScrabbleApp.APP_TITLE)
        self._root.geometry(ScrabbleApp.WINDOW_SIZE)
        self._root.resizable(0, 0)
        self._root.configure(borderwidth=10, bg=ScrabbleApp.STANDARD_BG)

    def _setup_tiles_images(self):
        self._tiles_imgs['_'] = tk.PhotoImage(file=f'./letters/_BLANK.png')
        for c in ascii_uppercase:
            self._tiles_imgs[c] = tk.PhotoImage(file=f'./letters/{c}.png')

    def _create_button(self, parent, on_press_func, image=None, text=None):
        # because many of Tkinter Button Widget configurations not working
        # on MAC OS, I was forced to create my own button from labels
        """
        creating a button from label with specific function
        :param parent: master widget
        :param on_press_func: the function to activate on click
        :param image: image to show on the button
        :param text: text to show on the button
        """
        button_name = tk.Label(parent, image=image, text=text,
                               font=ScrabbleApp.FONT_1, bg=ScrabbleApp.STANDARD_BG)
        button_name.bind("<Enter>",
                         lambda event: button_name.config(bg=ScrabbleApp.SUB_BG))
        button_name.bind("<Leave>", lambda event: button_name.config(
            bg=ScrabbleApp.STANDARD_BG))
        button_name.bind('<Button-1>', lambda event: button_name.config(
            relief=tk.SUNKEN))
        button_name.bind('<ButtonRelease-1>',
                         lambda event: on_press_func(event, button_name))
        return button_name

    def _create_wrapping_frame(self):
        """
        creates wrapping frame, which contains the main frames of the game
        """
        self._wrapper = tk.Frame(self._root, bg=ScrabbleApp.SUB_BG, bd=3)
        self._wrapper.pack(fill=tk.BOTH, expand=True)
        self._wrapper.columnconfigure(0, weight=1)
        self._wrapper.rowconfigure(0, weight=1)

    def _create_frame(self, name: str):
        frame = tk.Frame(self._wrapper, bg=ScrabbleApp.STANDARD_BG,
                         width=1200, height=700)
        frame.grid(row=0, column=0, columnspan=2, rowspan=2, sticky='news')
        self._game_frames[name] = frame

    def _raise_frame(self, frame):
        """
        this functions raises the wanted frame from those who were packed
        one above one
        """
        frame.tkraise()
        self._current_frame = frame

    ############################
    ##  CREATING MAIN SCREEN  ##
    ############################

    def _creat_main_screen(self):
        self._create_frame('main screen')
        parent = self._game_frames['main screen']

        # creating main logo
        self._logo_image = tk.PhotoImage(file=ScrabbleApp.LOGO_IMAGE)
        self._subtitle_image = tk.PhotoImage(file=ScrabbleApp.SUBTITLE_IMAGE)
        self._create_scrabble_image(parent)

        # creating pdf video html buttons
        self._video_image = tk.PhotoImage(file=ScrabbleApp.VIDEO_IMAGE)
        self._pdf_image = tk.PhotoImage(file=ScrabbleApp.PDF_IMAGE)
        self._html_image = tk.PhotoImage(file=ScrabbleApp.HTML_IMAGE)
        self._about_image = tk.PhotoImage(file=ScrabbleApp.ABOUT_IMAGE)
        self._create_pdf_video_html_buttons(parent)

        # creating exit button
        self._home_image = tk.PhotoImage(file=ScrabbleApp.HOME_IMAGE)
        self._exit_image = tk.PhotoImage(file=ScrabbleApp.EXIT_IMAGE)
        self._create_main_exit(parent)

        # creating game options buttons
        self._create_options(parent)

        # create about
        self._male_image = tk.PhotoImage(file=ScrabbleApp.MALE_IMAGE)
        self._female_image = tk.PhotoImage(file=ScrabbleApp.FEMALE_IMAGE)
        self._create_about_page()

        self._raise_frame(parent)

    def _create_scrabble_image(self, parent):
        logo_label = tk.Label(parent, image=self._logo_image, bg=ScrabbleApp.STANDARD_BG)
        logo_label.place(relx=0.00, rely=0.0)

        title_label = tk.Label(parent, image=self._subtitle_image, bg=ScrabbleApp.STANDARD_BG,
                               width=550)
        title_label.place(relx=0.06, rely=0.52)

    def _create_options(self, parent):
        greedy_button = self._create_button(parent, self._greedy_button, text='Greedy Approach')
        greedy_button.place(relwidth=0.3, relheight=0.1, relx=0.65, rely=0.25)

        mcts_button = self._create_button(parent, self._MCTS_button,
                                          text='Monte Carlo Tree Search')
        mcts_button.place(relwidth=0.3, relheight=0.1, relx=0.65, rely=0.4)

        minimax_button = self._create_button(parent, self._MiniMax_button,
                                             text='Adversarial Search')
        minimax_button.place(relwidth=0.3, relheight=0.1, relx=0.65, rely=0.55)

    def _create_pdf_video_html_buttons(self, parent):
        pdf_frame = tk.Frame(parent, height=100, width=100, bd=2)
        pdf_frame.pack_propagate(False)
        pdf_frame.place(relx=0.1, rely=0.7)
        pdf_button = self._create_button(pdf_frame, self._pdf_report, self._pdf_image)
        pdf_button.pack(fill=tk.BOTH, expand=True)

        html_frame = tk.Frame(parent, height=100, width=100, bd=2)
        html_frame.pack_propagate(False)
        html_frame.place(relx=0.2, rely=0.7)
        html_button = self._create_button(html_frame, self._html_report, self._html_image)
        html_button.pack(fill=tk.BOTH, expand=True)

        video_frame = tk.Frame(parent, height=100, width=100, bd=2)
        video_frame.pack_propagate(False)
        video_frame.place(relx=0.3, rely=0.7)
        video_button = self._create_button(video_frame, self._video_report, self._video_image)
        video_button.pack(fill=tk.BOTH, expand=True)

        about_frame = tk.Frame(parent, height=100, width=100, bd=2)
        about_frame.pack_propagate(False)
        about_frame.place(relx=0.4, rely=0.7)
        about_button = self._create_button(about_frame, self._about_us, self._about_image)
        about_button.pack(fill=tk.BOTH, expand=True)

    def _create_main_exit(self, parent):
        exit_frame = tk.Frame(parent, height=50, width=50, bd=2)
        exit_frame.pack_propagate(False)
        exit_frame.place(relx=0.0, rely=0.0)

        self._quit_button = self._create_button(exit_frame, self._quit_game,
                                                self._exit_image)
        self._quit_button.pack(fill=tk.BOTH, expand=True)

    ###############################
    ##  CREATING REPORT BUTTONS  ##
    ###############################

    def _pdf_report(self, event, parent):
        parent.config(relief=tk.FLAT)
        # getting location of the mouse
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if the mouse is still on the button
        if widget == parent:
            webbrowser.open(url='https://drive.google.com/file/d'
                                '/14qnoztkUyz3hlQ__Hy5XitvdAT6vReYw/view?usp=sharing', new=1)

    def _html_report(self, event, parent):
        parent.config(relief=tk.FLAT)
        # getting location of the mouse
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if the mouse is still on the button
        if widget == parent:
            # TODO
            webbrowser.open(url='https://www.google.com', new=1)

    def _video_report(self, event, parent):
        parent.config(relief=tk.FLAT)
        # getting location of the mouse
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if the mouse is still on the button
        if widget == parent:
            # TODO
            pass

    def _about_us(self, event, parent):
        parent.config(relief=tk.FLAT)
        # getting location of the mouse
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if the mouse is still on the button
        if widget == parent:
            # self._male_image = tk.PhotoImage(file='male.png')
            # self._female_image = tk.PhotoImage(file='female.png')
            # self._create_about_page()
            self._raise_frame(self._game_frames['about'])

    def _create_about_page(self):
        self._create_frame('about')
        parent = self._game_frames['about']
        menu_frame = tk.Frame(parent, bg=ScrabbleApp.STANDARD_BG, bd=2)
        menu_frame.place(relwidth=0.1, relheight=0.1, relx=0.0, rely=0.0)
        self._create_control_buttons(menu_frame)

        title = tk.Label(parent, text='Who are we .. ', font=('Georgia', 30, 'bold'),
                         bg=ScrabbleApp.SUB_BG, width=20, bd=2, relief=tk.GROOVE)
        title.pack(pady=(20, 10), ipady=10)

        frame = tk.Frame(parent, bd=2)
        frame.pack(fill=tk.BOTH, expand=True)
        upper = tk.Frame(frame, bd=2)
        upper.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower = tk.Frame(frame, bd=2)
        lower.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Label(upper, image=self._male_image, bg=ScrabbleApp.RAISED_CUBE_BG,
                 bd=2).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(upper, text='Muaz\n\nAbdeen', font=('Georgia', 30, 'bold'),
                 bg=ScrabbleApp.RAISED_CUBE_BG, bd=2).pack(side=tk.LEFT, fill=tk.BOTH,
                                                           expand=True)
        tk.Label(upper, image=self._male_image, bg=ScrabbleApp.RAISED_CUBE_BG,
                 bd=2).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(upper, text='Alon\n\nTifferet', font=('Georgia', 30, 'bold'),
                 bg=ScrabbleApp.RAISED_CUBE_BG, bd=2).pack(side=tk.LEFT, fill=tk.BOTH,
                                                           expand=True)

        tk.Label(lower, image=self._female_image, bg=ScrabbleApp.RAISED_CUBE_BG,
                 bd=2).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(lower, text='Liat\n\nRefaeli', font=('Georgia', 30, 'bold'),
                 bg=ScrabbleApp.RAISED_CUBE_BG, bd=2).pack(side=tk.LEFT, fill=tk.BOTH,
                                                           expand=True)
        tk.Label(lower, image=self._male_image, bg=ScrabbleApp.RAISED_CUBE_BG,
                 bd=2).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(lower, text='Or\n\nKatz ', font=('Georgia', 30, 'bold'),
                 bg=ScrabbleApp.RAISED_CUBE_BG, bd=2).pack(side=tk.LEFT, fill=tk.BOTH,
                                                           expand=True)

    ###########################
    ##  QUIT & MENU BUTTONS  ##
    ###########################

    def _to_menu(self, event, parent):
        """
        the function that activated when HOME button is pressed, it
        returns the player to the start menu
        """
        parent.config(relief=tk.FLAT)
        # getting location of the mouse
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if the mouse is still on the button
        if widget == parent:
            if self._current_frame not in [self._game_frames['main screen'],
                                           self._game_frames['about']]:
                if tk.messagebox.askquestion('Return to menu',
                                             'Are you sure?\nThis will terminate the game.',
                                             icon='warning') == 'yes':
                    self._current_frame.destroy()
                    self._raise_frame(self._game_frames['main screen'])
            else:
                self._raise_frame(self._game_frames['main screen'])

    def _quit_game(self, event, parent):
        """
        the function that activated when EXIT button is pressed, it quit
        the main window of the game
        """
        parent.config(relief=tk.FLAT)
        # getting location of the mouse
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if the mouse still on the button
        if widget == parent:
            if tk.messagebox.askquestion(ScrabbleApp.EXIT_TITLE,
                                         ScrabbleApp.EXIT_MESSAGE,
                                         icon='warning') == 'yes':
                self._root.destroy()
                sys.exit(0)

    def _create_control_buttons(self, parent):
        """
        creates HOME button, which taking player back to start menu,
        and EXIT button, wich quits the game
        """
        buttons_frame = tk.Frame(parent, height=50, bd=2)
        buttons_frame.pack_propagate(False)
        buttons_frame.pack(side=tk.TOP, fill=tk.BOTH)

        # home button
        self._create_button(buttons_frame, self._to_menu,
                            self._home_image).pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # quit button
        # I wil use it later so I assigned it to an instance variable
        self._quit_button = self._create_button(buttons_frame, self._quit_game,
                                                self._exit_image)
        self._quit_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    ############################
    ##  CREATING GAME SCREEN  ##
    ############################

    def _menu_frame(self, parent):
        menu_frame = tk.Frame(parent, bg=ScrabbleApp.STANDARD_BG, bd=2)
        menu_frame.place(relwidth=0.1, relheight=1, relx=0.0, rely=0.0)
        self._create_control_buttons(menu_frame)
        self._ver_logo = tk.PhotoImage(file=ScrabbleApp.VER_LOGO_IMAGE)
        logo_label = tk.Label(parent, image=self._ver_logo, bg=ScrabbleApp.STANDARD_BG)
        logo_label.place(relx=0.02, rely=0.15)

    def _score_widget(self, parent):
        score_frame = tk.Frame(parent, bg=ScrabbleApp.SUB_BG, bd=5)
        score_frame.place(relx=0.20, rely=0.15)

        p1_score_frame = tk.Frame(score_frame, bg=ScrabbleApp.STANDARD_BG)
        p1_score_frame.pack(fill=tk.BOTH, expand=True)
        p1_score_val = self._display_score(p1_score_frame)

        return p1_score_val

    def _display_score(self, parent):
        score_val = tk.StringVar()
        score_val.set('0')
        score_title = tk.Label(parent, text='SCORE', font=ScrabbleApp.FONT_3,
                               width=10, bg=ScrabbleApp.STANDARD_BG, bd=3)
        score_title.pack(ipadx=3, ipady=3, pady=(10, 0))
        score_frame = tk.Frame(parent, height=2, bd=4, relief=tk.SUNKEN)
        score_frame.pack(pady=(0, 10), padx=10)
        score = tk.Label(score_frame, height=2, width=10, font=ScrabbleApp.FONT_3,
                         textvariable=score_val,
                         fg=ScrabbleApp.SCORE_TIME_FG, bg=ScrabbleApp.SUB_IN_BG)
        score.pack()

        return score_val

    def _display_rack(self, parent, rack: str, player: str):
        rack_label = tk.Label(parent, text=f' {player}\'s Rack', font=ScrabbleApp.FONT_3,
                              bg=ScrabbleApp.STANDARD_BG, bd=2)
        rack_label.place(relx=0.2, rely=0.4)
        rack_frame = tk.Frame(parent, bg='saddle brown', bd=2)
        rack_frame.place(relx=0.15, rely=0.45)

        for i in range(7):
            self._init_cube(rack_frame, (0, i), color='saddle brown')
        for j in range(len(rack)):
            self._init_cube(rack_frame, (0, j), image=self._tiles_imgs[rack[j]],
                            color='saddle brown')

        return [(rack_label, rack_frame)]

    def _one_play_button(self, parent):
        start_frame = tk.Frame(parent, height=120, width=280)
        start_frame.pack_propagate(False)
        start_frame.place(relx=0.15, rely=0.6)
        return start_frame

    def _init_cube(self, parent, coords, color=RAISED_CUBE_BG,
                   image=None, text=None):
        if image:
            cube_label = tk.Label(parent, image=image, bg=color, width=6, height=3, bd=1,
                                  text=text, font=ScrabbleApp.FONT_5, compound='center')
        else:
            cube_label = tk.Label(parent, image=image, text=text, font=ScrabbleApp.FONT_4,
                                  bg=color, width=6, height=3,
                                  bd=1, relief=tk.GROOVE)

        cube_label.grid(row=coords[0], column=coords[1], sticky='news')

        # cube_label.bind("<Button-1>", lambda event: self._on_click(
        #     event, cube_label))
        return cube_label

    def _init_cubes_board(self, parent):
        rows = 15
        columns = 15
        board_frame = tk.Frame(parent, height=450, width=450, bd=4,
                               relief=tk.GROOVE,
                               bg=ScrabbleApp.CUBES_BOARD_BG)
        board_frame.pack(side=tk.RIGHT, padx=10, pady=(10, 15))
        for i in range(rows * columns):
            if ScrabbleApp.BOARD[i] in ScrabbleApp.BONUS_TILES:
                if ScrabbleApp.BOARD[i] == '*':
                    color = ScrabbleApp.BONUS_TILES[ScrabbleApp.BOARD[i]][0]
                    self._star_image = tk.PhotoImage(file=ScrabbleApp.STAR_IMAGE)
                    self._init_cube(board_frame, (i // columns, i % columns),
                                    color=color, image=self._star_image)
                else:
                    color = ScrabbleApp.BONUS_TILES[ScrabbleApp.BOARD[i]][0]
                    text = ScrabbleApp.BONUS_TILES[ScrabbleApp.BOARD[i]][1]
                    self._init_cube(board_frame, (i // columns, i % columns),
                                    color=color, text=text)
            else:
                self._init_cube(board_frame, (i // columns, i % columns))

        return board_frame

    def _update_board(self, board_frame, board: Board):
        for row in range(1, 16):
            for col in range(1, 16):
                idx = row * 17 + col
                if board[idx] not in EMPTY:
                    sq = board[idx]
                    new_idx = (row - 1) * 15 + (col - 1)
                    x, y = new_idx // 15, new_idx % 15
                    if sq.isupper():
                        self._init_cube(board_frame, (x, y), image=self._tiles_imgs[sq])
                    else:
                        self._init_cube(board_frame, (x, y), image=self._tiles_imgs['_'],
                                        text=sq)

    def _update_rack(self, rack_frame, p: Player):
        for i in range(7):
            self._init_cube(rack_frame, (0, i), color='saddle brown')
        for j in range(len(p.rack)):
            self._init_cube(rack_frame, (0, j), image=self._tiles_imgs[p.rack[j]],
                            color='saddle brown')

    def _update_score(self, score_frame, p: Player):
        score_frame.set(p.score)

    def _create_game(self, option: str):
        self._create_frame(option)
        game = self._game_frames[option]
        text = ' MONTE  CARLO  SIMULATION ' if option == 'MCTS' else option
        frame_title = tk.Label(game, text=text,
                               font=ScrabbleApp.FONT_1,
                               bg=ScrabbleApp.SUB_BG, bd=2, relief=tk.GROOVE)
        frame_title.pack(pady=(20, 20))
        self._menu_frame(game)
        scores = [self._score_widget(game)]
        # scores = list(self._score_widget(game, *self._players_names(option)))
        racks = self._display_rack(game, '', option)
        board = self._init_cubes_board(game)
        return board, racks, scores

    def _players_names(self, option: str):
        if option == 'Greedy': return 'Greedy', ''
        if option == 'MCTS':
            return 'MCTS', ''
        elif option == 'MiniMax':
            return 'MiniMax', ''

    ################################
    ##  PLAYING WAYS: ONE, WHOLE  ##
    ################################

    def _one_round(self, board, board_frame, racks_widgets, scores_StringVar):
        old_board = self._board.clone()

        for idx in range(len(self._board.players)):
            self._board.cur_p_idx = idx
            p = self._board.players[idx]
            play = p.strategy(self._board)
            self._board.make_one_play(play, verbose=True)
            # make gui display: rack, board, score
            self._update_board(board_frame, self._board)
            rack_label, rack_frame = racks_widgets[idx][0], racks_widgets[idx][1]
            self._update_rack(rack_frame, p)
            self._update_score(scores_StringVar[idx], p)

            if p.rack == '':
                self._game_over = True
                return [p.score for p in self._board.players]

        if old_board == self._board and self._board.all_exchanges < 0:
            # No player has a move; game over
            self._game_over = True
            return [p.score for p in self._board.players]

    ##########################
    ##  CREATE GREEDY GAME  ##
    ##########################
    def _greedy_button(self, event, parent):
        parent.config(relief=tk.FLAT)
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if mouse still on the button
        if widget == parent:
            self._create_greedy_game()
            self._raise_frame(self._game_frames['Greedy'])

    def _create_greedy_game(self):
        board_frame, racks, scores_StringVar = self._create_game('Greedy')
        greedy_game = self._game_frames['Greedy']
        self._game_over = self._playing = False
        self._board = Board(BOARD, [Player('GREEDY', AI.greedy)])

        def _play_one_greedy(event, parent):
            parent.config(relief=tk.FLAT)
            x, y = self._root.winfo_pointerxy()
            widget = self._root.winfo_containing(x, y)
            if widget == parent and not self._game_over:
                self._playing = True
                scores = self._one_round(self._board, board_frame, racks, scores_StringVar)
                if self._game_over:
                    for idx in range(len(self._board.players)):
                        p = self._board.players[idx]
                        p.score = scores[idx]
                        self._update_score(scores_StringVar[idx], p)
                    self._display_results(self._board.players)
            elif widget == parent and self._game_over:
                self._display_results(self._board.players)

        one_play_frame = self._one_play_button(greedy_game)
        self._once_img = tk.PhotoImage(file=ScrabbleApp.PLAY_IMAGE)
        one_play_frame = self._create_button(one_play_frame, _play_one_greedy, image=self._once_img)
        one_play_frame.pack(fill=tk.BOTH, expand=True)

    ########################
    ##  CREATE MCTS GAME  ##
    ########################

    def _MCTS_button(self, event, parent):
        parent.config(relief=tk.FLAT)
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if mouse still on the button
        if widget == parent:
            self._create_mcts_game()
            self._raise_frame(self._game_frames['MCTS'])

    def _create_mcts_game(self):
        board_frame, racks, scores_StringVar = self._create_game('MCTS')
        # rack_label, rack_frame = racks[0][0], racks[0][1]
        mcts_game = self._game_frames['MCTS']
        self._game_over = self._playing = False
        self._board = Board(BOARD, [Player('MCTS', AI.UCT)])

        def _play_one_mcts(event, parent):
            parent.config(relief=tk.FLAT)
            x, y = self._root.winfo_pointerxy()
            widget = self._root.winfo_containing(x, y)
            if widget == parent and not self._game_over:
                self._playing = True
                scores = self._one_round(self._board, board_frame, racks, scores_StringVar)
                if self._game_over:
                    for idx in range(len(self._board.players)):
                        p = self._board.players[idx]
                        p.score = scores[idx]
                        self._update_score(scores_StringVar[idx], p)
                    self._display_results(self._board.players)
            elif widget == parent and self._game_over:
                self._display_results(self._board.players)

        one_play_frame = self._one_play_button(mcts_game)
        self._once_img = tk.PhotoImage(file=ScrabbleApp.PLAY_IMAGE)
        one_play_frame = self._create_button(one_play_frame, _play_one_mcts, image=self._once_img)
        one_play_frame.pack(fill=tk.BOTH, expand=True)

    ###########################
    ##  CREATE MiniMax GAME  ##
    ###########################

    def _MiniMax_button(self, event, parent):
        parent.config(relief=tk.FLAT)
        x, y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x, y)
        # if mouse still on the button
        if widget == parent:
            self._create_minimax_game()
            self._raise_frame(self._game_frames['MiniMax'])

    def _create_minimax_game(self):
        board_frame, racks, scores_StringVar = self._create_game('MiniMax')
        # rack_label, rack_frame = racks[0][0], racks[0][1]
        minimax_game = self._game_frames['MiniMax']
        self._board = Board(BOARD, [Player('MiniMax', AI.expictimax)])

        def _play_one_minimax(event, parent):
            parent.config(relief=tk.FLAT)
            x, y = self._root.winfo_pointerxy()
            widget = self._root.winfo_containing(x, y)
            if widget == parent and not self._game_over:
                self._playing = True
                scores = self._one_round(self._board, board_frame, racks, scores_StringVar)
                if self._game_over:
                    for idx in range(len(self._board.players)):
                        p = self._board.players[idx]
                        p.score = scores[idx]
                        self._update_score(scores_StringVar[idx], p)
                    self._display_results(self._board.players)
            elif widget == parent and self._game_over:
                self._display_results(self._board.players)

        one_play_frame = self._one_play_button(minimax_game)
        self._once_img = tk.PhotoImage(file=ScrabbleApp.PLAY_IMAGE)
        one_play_frame = self._create_button(one_play_frame, _play_one_minimax,
                                             image=self._once_img)
        one_play_frame.pack(fill=tk.BOTH, expand=True)

    def _display_results(self, players: List[Player]):
        tk.messagebox.showinfo('RESULTS', self._game_summary(players))

    def _game_summary(self, players: List[Player]):
        res = []
        winner = ('', 0)
        for p in players:
            res.append((p.name, p.score))
            winner = (p.name, p.score) if p.score > winner[1] else winner
        return f'The game is over.\n' \
               f'{winner[0]} wins with {winner[1]} points\n'


def choose_board(strategy: int):
    if strategy == 1:
        return Board(BOARD, [Player('Greedy', AI.greedy)])
    elif strategy == 2:
        return Board(BOARD, [Player('MCTS', AI.UCT)])
    elif strategy == 3:
        return Board(BOARD, [Player('MiniMax', AI.expictimax)])


def main(gui: bool = True):
    if not gui:
        strategy = 0
        while strategy not in [1, 2, 3]:
            strategy = int(input("choose your strategy: 1, 2 or 3\n"
                                 "(1) Greedy strategy.\n"
                                 "(2) MCTS strategy.\n"
                                 "(3) MiniMax strategy.\n"))
        board = choose_board(strategy)
        play_game(board)

    else:
        root = tk.Tk()
        ScrabbleApp(root)
        root.mainloop()


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1 or (len(args) == 1 and args[0] != 'GUI'):
        print('Usage: python3 Scrabble.py [optional: GUI]:\n'
              'Example: python3 Scrabble.py GUI\n'
              '         python3 Scrabble.py')
    gui = False if len(args) == 0 else True
    main(gui)

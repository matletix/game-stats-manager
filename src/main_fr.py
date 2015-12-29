# -*- coding: utf-8 -*-
##------ IMPORTS ------##
import os, sys, datetime, time
sys.path.append('E:/v0.2/src')
import module_locator
import PIL.ImageGrab, PIL.Image, PIL.ImageTk
import webbrowser
from tkinter import *
from tkinter import tix, filedialog, messagebox, simpledialog

##------ VAR ------##
"""Description :
    'MY_PATH' is the path of the final executable
    'SAVE_TEMP_PATH' is the path of the saved templates
    'SAVE_GAME_PATH' is the path of the saved games
    'SAVE_STATS_PATH' is the path of the saved statistics
    'CONFIG_PATH' it the path of the configuration file
    'date', 'day', 'month' and 'year' contain data about the date at which
        the executable was launched
    'MAX_TS contains the maximum number of time divisions
    'DEFAULT_TS contains the default number of time divisions
    'DEFAULT_CATEGORIES contains the default categories
    'sport' contains the list of predefined game templates
"""

MY_PATH = module_locator.module_path()
SAVE_TEMP_PATH = MY_PATH + '/templates'
SAVE_GAME_PATH = MY_PATH
SAVE_STATS_PATH = MY_PATH
CONFIG_PATH = MY_PATH + '/config.txt'
REPOSITORY_URL = "https://gitlab.com/mrollet/game-stats-manager/wikis/doc"
VERSION = 1.0
YEARS = '2015, 2016'
AUTHORS = 'Mathieu Rollet'
CONTACT = 'rollet.mathieu@openmailbox.org'

# Gather current date
date = datetime.datetime.now()
day = str(date.day) if len(str(date.day)) == 2 else '0'+str(date.day)
month = str(date.month) if len(str(date.month)) == 2 else '0'+str(date.month)
year = str(date.year)

MAX_NB_PLAYERS = 99
MAX_TS = 20
GREEN, RED, BLACK, WHITE = 'green', 'red', 'black', 'white'
DEFAULT_ACTIVITY = 'basketball'
DEFAULT_NBPLAYERS = 10
DEFAULT_TS = 1
DEFAULT_CATEGORIES = [("Aucune catégorie, créez les vôtre ou chargez un jeu", False)]

sports = []
sports.append({'name': 'Basketball', 'nbPlayers': 10, 'timeSplit': 4,
              'categories': [("Tir 2pts", True), ("Tir 3pts", True), ("Lancer franc", True), 
                             ("Ballon perdu", False), ("Assiste", False), ("Rebond off", False),
                             ("Rebond def", False), ("Vole", False), ("Bloque", False)]})

sports.append({'name': 'Football', 'nbPlayers': 11, 'timeSplit':2, 
               'categories': [("But", True), ("Tackle", True), ("Drible", True), 
                             ("Assiste", False), ("Receiptionne", False),
                             ("Vole", False), ("Bloque", False)]})
              
###############    BACKEND    #############
##------ CLASSES ------##
class Player:
    """This class represents a player of the game. The 'playercount' class
    variable stores the total number of players currently playing.
    """
    playercount = 0
    def __init__(self, game, name=None):
        """Initialize the player name to the given name if any, or to a number
        if not. Initialize the player score row to zeros
        """
        self.name = StringVar()
        self.name.set(name if name else str(Player.playercount+1))
        self.score = [IntVar() for c in range(game.h.nbCat)]
        Player.playercount += 1

class Categorie:
    """This class represents a categorie (a column) with a name (the 'value')
    and a 'tick', which can take the values None, True or False. If True, then
    the categorie will be represented with a '✓' (success) tick in its name, if 
    False, it will be represented with a '✗' (fail) tick. If None, the
    representation of the categorie is not affected.
    """
    def __init__(self, value):
        self.value = value
        self.tick = None
    
    def __repr__(self):
        return str.__str__(self.value)

class Header:
    """Class representing the header headband of the table, containing the name
    of the differents categories. If a categorie is associated with a 'dual'
    boolean set to True, it is considered dual and two categories are effectively
    created : one with the tick attribute set to True, the other with the tick
    attribute set to False. If 'dual' is given to False, a single categorie is
    created with the tick attribute set to None.
    The 'cat' attribute contains the categories header.
    The 'col' attribute contains the 'Player' attribute and the 'cat' categories
    """
    def __init__(self, categories):
        self.cat = []
        self.col = ['Joueurs']
        if categories:
            for cat, dual in categories:
                if dual:
                    c1 = Categorie(cat + ' ✓')
                    c2 = Categorie(cat + ' ✗')
                    c1.tick = True
                    c2.tick = False
                    self.cat.append(c1)
                    self.cat.append(c2)
                else:
                    c = Categorie(cat)
                    c.tick = None
                    self.cat.append(c)
        else:
            c = Categorie("Aucune catégorie, créez les vôtre ou chargez un jeu")
            self.cat.append(c)
        
        self.col.extend(self.cat)
        self.nbCat = len(self.cat)
        self.nbCol = len(self.col)
 
class Game:
    """Class containing the hole data of a game and a set of methods to interact
    with it.
        'activity' contains the name of the sport
        'team' contains the name of the monitored team
        'opponent' contains the name of the opponent team
        'nbPlayers' contains the number of players monitored
        'categories' contains the list of tuples (categorie_name, dual)
        'h' contains the Header object representing the header of the table
        'players' contains the list of monitored Players objects
        'timeSplit' contains the number of time divisions that make a all game
        'tsScore' (timeSplitScores) contains the total score table for every
            time division plus the entire time score table. It's a 3D matrix with
            the first dimension being the time division, and the two others being
            the two dimensions of the score table. For a soccer match with
            two halves, tsScore[0] is the score table of the first half,
            tsScore[1] the score table of the second half, and tsScore[2] the
            score table of both halves.
        'score' contains the score table currently displayed to the user and
            with which he interacts by adding and removing points
        'currentTs' contains the current time division
        'freezed' is a boolean that is True if the match is over, else False
    """
    
    def __init__(self, root,
                 activity=DEFAULT_ACTIVITY, 
                 team='', 
                 opponent='', 
                 nbPlayers=DEFAULT_NBPLAYERS,
                 categories=DEFAULT_CATEGORIES,
                 timeSplit=DEFAULT_TS
                ):
        Player.playercount = 0
        self.activity = activity
        self.team = StringVar()
        self.opponent = StringVar()
        self.team.set(team)
        self.opponent.set(opponent)
        self.nbPlayers = nbPlayers
        self.categories = categories
        self.h = Header(categories)
        self.players = [Player(self) for i in range(self.nbPlayers)]
        self.timeSplit = timeSplit
        self.tsScore = [[[0] * self.h.nbCat for r in range(self.nbPlayers)] for i in range(timeSplit+1)]
        self.score = [p.score for p in self.players]
        self.currentTs = IntVar()
        self.freezed = False
    
    def __repr__(self):
        args = (self.currentTs.get(), [[cell.get() for cell in row] for row in self.score])
        kwargs = self.__dict__
        
        return ("activity : {activity}\n"
                "team : {team}\n"
                "opponent : {opponent}\n"
                "nbPlayers : {nbPlayers}\n"
                "players : {players}\n"
                "nbCat : {h.nbCat}\n"
                "header : {h.col}\n"
                "timeSplit : {timeSplit}\n"
                "freezed = {freezed}\n"
                "currentTs = {}\n"
                "score = {}\n"
               ).format(*args, **kwargs)
        
    def set_players(self, playerNames=None):
        """Method to set players name. 'playerNames' is a list of strings.
        If not given, numbers are automatically given to players as names
        """
        if playerNames:
            for i in range(len(playerNames)):
                self.players[i].name.set(playerNames[i])
        else:
            for i in range(self.nbPlayers):
                self.players[i].name.set(str(i+1))
        
    def reset_score(self):
        """Reset the 'score' grid to zeros."""
        for p in self.players:
            for s in p.score:
                s.set(0)
    
    def reset_game(self):
        """Function that reset to zeros all scores of every time period stored in
        the 'tsScore' attribute as well as the 'score' grid.
        """
        self.tsScore = [[[0] * self.h.nbCat for r in range(self.nbPlayers)] for i in range(self.timeSplit+1)]
        self.reset_score()
        self.currentTs.set(0)
        self.freezed = False
            
    def chgTs(self, i):
        """Function that copy the 'score' table to the correspondant time period
        of 'tsScore' and reinitialize the 'score' grid.
        'i' is a integer that contains the new time division.
        """
        if not self.freezed:
            # when the '0' time division is clicked, the score is reinitialized
            if i == 0:
                self.reset_score()
            else:
                for r in range(self.nbPlayers):
                    for c in range(self.h.nbCat):
                        # save the score grid to the corresponding tsScore time division
                        self.tsScore[i-1][r][c] = self.score[r][c].get()
                        if i < self.timeSplit:
                        # reset the score interface except if the EOM button has been clicked
                            self.score[r][c].set(0)
                        else:
                            self.tsScore[-1][r][c] = sum([self.tsScore[i][r][c] for i in range(self.timeSplit)])
                            self.freezed = True
    
    def chgNbPlayers(self, root):
        """Generate an interactive window that allow to change the number of players
        and to reinitialize the score table accordingly
        """    
        msg = ("Attention : cette action va réinitialiser les scores\n\n"
            "Entrer le nombre de joueurs à affichuer : ")
        newNb = simpledialog.askinteger("Nombre de joueurs", msg, minvalue=1, maxvalue=MAX_NB_PLAYERS)
        if newNb:
            self.set_newgame(root, nbPlayers=newNb, 
                        categories=self.categories,
                        activity=self.activity,
                        team=self.team.get(),
                        opponent=self.opponent.get(),
                        timeSplit=self.timeSplit
                    )
    
    def chgNbTs(self, root):
        """Generate an interactive window that allow to change the number of time
        divisions and to reinitialize the interface accordingly
        """
        msg = ("Attention : cette action va réinitialiser les scores\n\n"
            "Entrer le nombre de périodes à considérer : ")
        newTs = simpledialog.askinteger("Nombre de périodes", msg, minvalue=1, maxvalue=MAX_TS)
        if newTs:
            self.set_newgame(root, nbPlayers=self.nbPlayers, 
                        categories=self.categories,
                        activity=self.activity,
                        team=self.team.get(),
                        opponent=self.opponent.get(),
                        timeSplit=newTs
                    )
    
    def chgHeader(self, root):
        """Generate an interactive window that allows to change the number and name of
        column headers and to reinitialize the score table accordingly
        """
        popup = chgHeaderWindow(self, root)
        
        # Handle the 'player' field
        CatConfigField.fields = []
        CatConfigField(popup.subFrame, self.h.col[0], False, 0)

        # Other fields
        for i,h in enumerate(self.categories):
            CatConfigField(popup.subFrame, h[0], h[1], i+1)        
        
        root.wait_window(popup)

    def gen_stats(self):
        """Generate stats according to the score stored in 'tsScore'. For every dual
        category, store the percentage of "successes" or "fails" in addition to
        the score. For non-dual categories, simply store the score.
        """
        stats = [[[] for r in range(self.nbPlayers+1)] for ts in range(self.timeSplit+1)]
        
        for i in range(self.timeSplit+1):
            for c, cat in enumerate(self.h.cat):
                for r in range(self.nbPlayers):
                    if cat.tick is True or cat.tick is False:
                        try:
                            if cat.tick is True:
                                percent = self.tsScore[i][r][c] / (self.tsScore[i][r][c] + self.tsScore[i][r][c+1]) * 100
                            else:
                                percent = self.tsScore[i][r][c] / (self.tsScore[i][r][c-1] + self.tsScore[i][r][c]) * 100
                        except ZeroDivisionError:
                            percent = 0
                        label = "{} ({} %)".format(self.tsScore[i][r][c], round(percent))
                    else:
                        label = str(self.tsScore[i][r][c])
                    
                    stats[i][r].append(label)
                
                # Total
                s = lambda c: sum([self.tsScore[i][r][c] for r in range(self.nbPlayers)])
                if cat.tick is True or cat.tick is False:
                    try:
                        if cat.tick is True:
                            percent = s(c) / (s(c) + s(c+1)) * 100
                        else:
                            percent = s(c) / (s(c-1) + s(c)) * 100
                    except ZeroDivisionError:
                        percent = 0
                    label = "{} ({} %)".format(s(c), round(percent))   
                                    
                else:
                    label = str(s(c))
                    
                stats[i][-1].append(label)
        return stats
    
    def set_newgame(self, root, playerNames=[], activity=DEFAULT_ACTIVITY,
                    team='', opponent='', nbPlayers=DEFAULT_NBPLAYERS,
                    categories=DEFAULT_CATEGORIES, timeSplit=DEFAULT_TS, **kwargs):
        """Set a all new game."""
        self.__init__(root, activity, team, opponent, nbPlayers, categories, timeSplit)
        if len(playerNames) == self.nbPlayers:
            self.set_players(playerNames)
        regen_interface(root, self)

##------ FUNCTIONS ------##
def save(game, data):
    """Open a file selector window, and save the game if data=='game' or the
    stats if data=='stats'. Return 0 if saved without error, 1 if the 
    procedure has been purposely cancelled by the user, or 2 if it has been aborted.
    """
    if data == 'stats':
        stats = game.gen_stats()
        initialdir = SAVE_STATS_PATH
    
    elif data == 'game':
        initialdir = SAVE_GAME_PATH
    
    # Set the default name depending on the 'team' variable
    if game.team.get():
        default_name = "{}-{}-{}-{}-{}.csv".format(data, game.team.get(), day, month, year)
    else:
        default_name = "{}-{}-{}-{}.csv".format(data, day, month, year)
        
    file_path = filedialog.asksaveasfilename(initialfile=default_name,
                                             initialdir=initialdir,
                                             filetype=(("CSV files", "*.csv"),
                                                       ("All files", "*.*")))
    if not file_path:
        # file_path is None if the filedialog box has been cancelled
        return 1
    
    try:
        with open(file_path, 'w+', encoding='utf-8') as file:
            # First write a metadata header depending on the 'data' variable
            file.write('DATE,{}/{}/{}\n'.format(day, month, year))
            if data == 'game':
                file.write('ACTIVITY,{}\n'.format(game.activity))
            if game.team.get():
                file.write('TEAM,{}\n'.format(game.team.get().strip()))
            else:
                file.write('TEAM,unknown\n')
            if game.opponent.get():
                file.write('OPPONENT,{}\n'.format(game.opponent.get().strip()))
            else:
                file.write('OPPONENT,unknown\n')
            if data == 'game':
                file.write('PLAYERS,{}\n'.format(','.join([p.name.get() for p in game.players])))
                file.write('CATEGORIES,{}\n'.format(';'.join([str(tupl) for tupl in game.categories])))
                file.write('TIME_PARTITIONS,{}\n'.format(game.timeSplit))
                file.write('CURRENT_PERIOD,{}\n\n'.format(game.currentTs.get()))
            else:
                file.write('\n')
            
            # Then write scores or stats for each period
            for q in range(game.timeSplit+2):
                # Write quarter
                if q == 0:
                    file.write('1st period\n')
                elif 0 < q < game.timeSplit:
                    file.write('{}e period\n'.format(str(q+1)))
                elif q == game.timeSplit:
                    file.write('Full\n')
                elif q == game.timeSplit+1 and data == 'game':
                    file.write('Current score\n')
                
                if q < game.timeSplit+1 or (q == game.timeSplit+1 and data == 'game'):
                    # Write headers
                    for i in range(game.h.nbCol-1):
                        file.write('{},'.format(game.h.col[i]))
                    file.write('{}\n'.format(game.h.col[-1]))   
                    
                    # Write scores or stats
                    for r in range(game.nbPlayers):
                        file.write('{},'.format(game.players[r].name.get()))
                        if q < game.timeSplit+1:
                            if data == 'game':
                                for c in range(game.h.nbCat - 1):
                                    file.write('{},'.format(game.tsScore[q][r][c]))
                                file.write('{}\n'.format(game.tsScore[q][r][-1]))
                            else:
                                for c in range(game.h.nbCat - 1):
                                    file.write('{},'.format(stats[q][r][c]))
                                file.write('{}\n'.format(stats[q][r][-1]))
                        else: 
                            for c in range(game.h.nbCat - 1):
                                file.write('{},'.format(game.score[r][c].get()))
                            file.write('{}\n'.format(game.score[r][-1].get()))
                
                    # Add the 'Team' row if stats
                    if data == 'stats':
                        file.write('Team,')
                        for c in range(game.h.nbCat-1):
                            file.write('{},'.format(stats[q][-1][c]))
                        file.write('{}\n'.format(stats[q][-1][-1]))
                    file.write('\n')
                
    except PermissionError as err:
        messagebox.showerror(message="Error : {}".format(err.args[-1]),
                             detail="Ensure that no other ressource is using this file and try again")
        return 2
    except FileNotFoundError as err:
        messagebox.showerror(message="Error : {}".format(err.args[-1]))
        return 2
    except OSError:
        messagebox.showerror('Invalid Name', 'Sorry, this file name is illegal. Operation cancelled.')
    else:
        return 0

def save_template(root, game):
    """Save the current configuration of the game in a game template"""
    if not os.path.exists(SAVE_TEMP_PATH):
        os.mkdir(SAVE_TEMP_PATH)
    
    name = ''
    while len(name) < 1:
        name = simpledialog.askstring('Nom du modèle',
                                  'Entrer un nom pour ce modèle (ex : "Basketball", "Hockey")')
        if name is None: 
            # askstring dialog returns None if cancelled
            return 1
        
        if len(name) < 1:
            messagebox.showinfo(title='Empty entry', message='Veuillez entrer un nom')
        
    if os.path.exists(SAVE_TEMP_PATH + '/{}.gsm'.format(name)):
        replace = messagebox.askokcancel(title='Attention', icon='warning', default='cancel',
                                         message="Un modèle avec ce nom existe déjà. Continuer l'écrasera.")
        if not replace:
            return 1
    try:
        with open(SAVE_TEMP_PATH + '/{}.gsm'.format(name), 'w+', encoding='utf-8') as f:
            f.write('CATEGORIES,{}\n'.format(';'.join([str(tupl) for tupl in game.categories])))
            f.write('TIME_PARTITIONS,{}\n'.format(game.timeSplit))
            f.write('NB_PLAYERS,{}\n'.format(game.nbPlayers))
    except OSError:
        messagebox.showerror('Invalid Name', 'Sorry, this file name is illegal. Operation cancelled.')
    else:
        # regenerate the root menu to display the saved template in the 'New' menu
        regen_menu(root, game)
        
        # save thumbnail
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        time.sleep(0.2)
        image = PIL.ImageGrab.grab((x, y, x+w, y+h))
        size = 600, 300
        image.thumbnail(size)
        image.save(SAVE_TEMP_PATH + "/{}.png".format(name))


def open_game(data, name=''):
    """Return data of a game previously saved with the 'save game' option if
    data=='game', or of a game template if data=='template'.
    """
    if data == 'game':
        filetypes=[("CSV files","*.csv")]
    elif data == 'template':
        filetypes=[("GSM files","*.gsm")]
    
    if not name:
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if not file_path:
            # If the 'Cancel' button has been clicked
            return 1
    else:
        file_path = SAVE_TEMP_PATH + '/{}.gsm'.format(name)
    
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            try:
                # Collect metadata
                if data == 'game':
                    metadata = ['DATE', 'ACTIVITY', 'TEAM', 'OPPONENT', 'PLAYERS', 'CATEGORIES', 'TIME_PARTITIONS', 'CURRENT_PERIOD']
                elif data == 'template':
                    metadata = ['CATEGORIES', 'TIME_PARTITIONS', 'NB_PLAYERS']
                for i in range(len(metadata)):
                    l = f.readline().strip()
                    assert l.startswith(metadata[i])
                    value = l[len(metadata[i])+1:]
                    metadata[i] = value
                
                if data == 'template':
                    activity, team, opponent, players = '', '', '', ''
                    categories = [eval(c) for c in metadata[0].split(';')]
                    timeSplit = int(metadata[1])
                    nbPlayers = int(metadata[2])
                    currentTs = 0
                    
                elif data == 'game':
                    activity = metadata[1]
                    team = metadata[2]
                    opponent = metadata[3]
                    players = metadata[4].split(',')
                    categories = [eval(c) for c in metadata[5].split(';')]
                    timeSplit = int(metadata[6])
                    currentTs = int(metadata[7])
                    nbPlayers = len(players)
                
                nbCat = len(categories)
                tsScore = [[[0] * nbCat for r in range(nbPlayers)] for q in range(timeSplit+1)]
                score = [[0 for c in range(nbCat)] for r in range(nbPlayers)]
                
                if data == 'game':
                    # Load 'game' and 'score'
                    for q in range(timeSplit+2):
                        for jumplines in range(3):
                            f.readline()
                        for r in range(nbPlayers):
                            l = f.readline().strip()
                            l = l.split(',')[1:]
                            if q <= timeSplit:
                                tsScore[q][r] = [int(i) for i in l]
                            else:
                                score[r] = [int(i) for i in l]
                
            except AssertionError:
                message = "Error : Invalid file format"
                detail = "Make sure that the file you try to open has been generated by the 'Save game' function of the 'File' menu of Game stats manager."
                messagebox.showerror(message=message, detail=detail)
                return 1
                
            except:
                message = "An error occured when trying to import the file"
                detail = "Make sure that the file you try to open has been generated by the 'Save game' function of the 'File' menu of Game stats manager."
                messagebox.showerror(message=message, detail=detail)
                return 1
                
    except FileNotFoundError as err:
        # 'If' condition to avoid creating an error dialog by trying to load an inexistant template at start
        if data != 'template':
            messagebox.showerror(message="Error : {}".format(err.args[-1]))
            return err.args[0]
        
    else:
        return activity, team, opponent, categories, tsScore, timeSplit, currentTs, nbPlayers, players, score

def load_game(root, game, data, name=''):
    """ Open a CSV file previously saved as a game by this programm and load the
    4 quarter scores, the quarter that was selected, and the score displayed on
    the interface.
    """
    if name:
        new_data = open_game(data, name)
    else:
        new_data = open_game(data)
        
    if new_data == 1:
        return 1
        
    activity, team, opponent, categories, tsScore, timeSplit, currentTs, nbPlayers, players, score = new_data
    game.set_newgame(root,
                     activity=activity,
                     team=team,
                     opponent=opponent,
                     nbPlayers=nbPlayers,
                     playerNames=players,
                     categories=categories,
                     timeSplit=timeSplit)
    
    if data == 'game':
        game.currentTs.set(currentTs)
        game.tsScore = tsScore
        for r, p in enumerate(game.players):
            for c in range(game.h.nbCat):
                p.score[c].set(score[r][c])
    
    if data == 'template':
        with open(CONFIG_PATH, 'w+', encoding='utf8') as f:
            f.write(SAVE_TEMP_PATH + '\n')
            f.write(SAVE_GAME_PATH + '\n')
            f.write(SAVE_STATS_PATH + '\n')
            f.write(name)

##############    FRONTEND    #############
##------ FUNCTIONS ------##
def foreground(cat):
    """Define the foreground color of a categorie depending on its tick attribute"""
    fg = BLACK
    if cat.tick is True:
        fg = GREEN
    elif cat.tick is False:
        fg = RED
    return fg

def tslabel(game):
    """Define the name of the time division depending on the number of divisions"""
    tslabels = {2: "Mi-temps : ", 4: "Quart-temps : "}
    try:
        text = tslabels[game.timeSplit]
    except KeyError:
        text = "Period : "
    return text

def regen_menu(root, game):
    """Regenerate the menu bar"""
    root.menu.grid_remove()
    root.menu = MainMenu(root, game)
    root.menu.grid(row=0, sticky=N+S+E+W)
    
def regen_interface(root, game):
    """Generate a new interface"""
    root.gframe.grid_remove()
    root.gframe = GameFrame(root, game)
    regen_menu(root, game)
    root.gframe.grid(row=1, sticky=N+S+E+W)
    
def show_stats(root, game):
    """Generate the stats table according to the number of players and the 
    column headers
    """
    statsWin = Toplevel()
    stats = game.gen_stats()
    ntb = tix.NoteBook(statsWin)
    if game.timeSplit > 1:
        tslb = tslabel(game)
        plabels = ["1st {}".format(tslb)]
        for i in range(2, game.timeSplit+1):
            plabels.append(str(i)+"e {}".format(tslb))
        plabels.append("Full time")
    else:
        plabels = ['Stats']
    pages = []
    for i,l in enumerate(plabels):
        ntb.add("page"+str(i+1), label=l)
        pages.append(ntb.subwidget_list["page"+str(i+1)])
    
    # Generating pages of quart time 
    for i in range(len(pages)):
        
        # Players column
        for r,p in enumerate(game.players):
            label = Label(pages[i], text=p.name.get(), bd=3, relief=RIDGE)
            label.grid(row=r+1, column=0, sticky=N+S+E+W)
        tot = Label(pages[i], text="Team", bd=3, relief=RIDGE)
        tot.grid(row=game.nbPlayers+1, column=0, sticky=N+S+E+W)
        
        # Headers
        for c,t in enumerate(game.h.col):
            Label(pages[i], text=t, bd=3, relief=RAISED).grid(row=0, column=c, sticky=N+S+E+W)
        
        # Stats
        for c in range(game.h.nbCat):
            for r in range(game.nbPlayers):
                stat = Label(pages[i], text=stats[i][r][c], relief=SUNKEN, bd=1, bg=WHITE)
                stat.grid(column=c+1, row=r+1, sticky=N+S+E+W)
            
            # Total
            lb = Label(pages[i], text=stats[i][-1][c], bd=2, relief=SUNKEN, bg=WHITE)
            lb.grid(row=game.nbPlayers+1, column=c+1, sticky=N+S+E+W)
                
        # Grid configuration
        for c in range(game.h.nbCat+1):
            Grid.columnconfigure(pages[i], c, weight=1)
        for r in range(game.nbPlayers+2):
            Grid.rowconfigure(pages[i], r, weight=1)
            
    ntb.grid(row=0, column=0, sticky=N+S+E+W)
    
    statsWin.title("Statistiques")
    Grid.rowconfigure(statsWin, 0, weight=1)
    Grid.columnconfigure(statsWin, 0, weight=1)
    statsWin.config(menu=MenuStats(statsWin, game))
    
    root.wait_window(statsWin)

def ManageTemplates(root, game):
    def rename(root, game, old, window):
        """Rename a template"""
        new = ''
        while len(new) < 1:
            new = simpledialog.askstring('Nouveau nom', 'Entrer un nom pour ce modèle')
            if new is None:
                return 1
            
            elif new == '':
                messagebox.showinfo('Invalid Entry', 'Please enter a name')
            
            else:
                try:
                    os.rename('{}/{}'.format(SAVE_TEMP_PATH, old), '{}/{}.gsm'.format(SAVE_TEMP_PATH, new))
                except OSError:
                    messagebox.showerror('Invalid Name', 'This name is illegal. Please try a different one')
                    new = ''
                else:
                    try:
                        os.rename('{}/{}.png'.format(SAVE_TEMP_PATH, old[:-4]), '{}/{}.png'.format(SAVE_TEMP_PATH, new))
                    except:
                        # no preview found
                        pass
                    
        window.destroy()
        # regenerate the root menu to display the template in the 'New' menu
        regen_menu(root, game)
        ManageTemplates(root, game)
                
    def remove(root, game, filename, labelframe, lfchildren):
        """Remove a template and its thumbnail"""
        try:
            os.remove('{}\{}'.format(SAVE_TEMP_PATH, filename))
            os.remove('{}\{}.png'.format(SAVE_TEMP_PATH, filename[:-4]))
        except FileNotFoundError:
            pass
        
        for widget in lfchildren:
            widget.destroy()
        
        Label(labelframe, text='Supprimé', justify=CENTER).grid(padx=100, pady=20)
        # regenerate the root menu to update the templates displayed in the 'New' menu
        regen_menu(root, game)
        
    
    window = Toplevel()
    window.title('Gérer les modèles')

    scrollbar = Scrollbar(window)
    canvas = Canvas(window, yscrollcommand=scrollbar.set)
    scrollbar.config(command=canvas.yview)
    frame = Frame(canvas)
    
    path, dirs, files = next(os.walk(SAVE_TEMP_PATH))
    gsmfiles = [f for f in files if f.endswith('.gsm')]
    
    # generate the frame grid
    if gsmfiles:
        for i, filename in enumerate(gsmfiles):
            strippedName = filename[:-4]
            lf = LabelFrame(frame, text=strippedName)
            lf.grid(row=i//2, column=i%2, ipadx=10, ipady=10, padx=10, pady=10)
            try:
                img = PIL.Image.open('{}/{}.png'.format(path, strippedName))
                # make the photo printable by the Label widget
                img = PIL.ImageTk.PhotoImage(img)
                l = Label(lf, image=img)
                # to avoid garbage-collection of the image
                l.image = img
            except FileNotFoundError:
                l = Label(lf, text="Pas d'aperçu disponible.\n Charger le modèle et l'enregistrer à nouveau pour en générer une.")
                
            btnframe = Frame(lf)
            rmbtn = Button(btnframe, text="Supprimer", command=lambda lf=lf, f=filename, l=[l, btnframe]: remove(root, game, f, lf, l))
            editbtn = Button(btnframe, text="Renommer", command=lambda path=path, old=filename: rename(root, game, old, window))
            editbtn.grid(row=0, column=0)
            rmbtn.grid(row=0, column=1)
            l.grid(row=0, column=0)
            btnframe.grid(row=1, column=0)
    else:
        Label(frame, text=("Il n'y a aucun modèle à gérer.\n Pour créer un modèle, configurer un jeu via le menu 'Edit' et l'enregistrer comme modèle via le menu 'Fichier'.")).grid()
    
    # get the frame width and height to generate a proper canvas
    frame.grid()
    frame.update_idletasks()
    width = frame.winfo_width()
    height = frame.winfo_height()
    frame.grid_remove()
    
    if height > 700:
        height = 700
    
    canvas.config(width=width, height=height)
    canvas.create_window((0, 0), window=frame, anchor='nw')
    canvas.config(scrollregion=canvas.bbox('all'))
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    scrollbar.grid(row=0, column=1, sticky=N+S+E+W)
    
    # make the window resizable
    Grid.rowconfigure(window, 0, weight=1)
    Grid.columnconfigure(window, 0, weight=1)
        
    window.mainloop()

def safeExit(root, game):
    """Ask if willing to save the game before exit"""
    msg = 'Sauvegarder le jeu en cours avant de quitter ?'
    s = messagebox.askyesnocancel(title='Exit', message=msg)
    if s:
        savefailed = save(game, 'game')
        if not savefailed:
            root.destroy()
    elif s == False:
        root.destroy()
    else:
        # if s == None (meaning Cancel has been clicked)
        pass
        
def browse(*event):
    webbrowser.open_new(REPOSITORY_URL)

def about():
    def viewLicense(whatToView):
        popup = Toplevel()
        # not resizable
        popup.resizable(0,0)
        
        if whatToView == "License":
            data = """This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU General Public License as published by the 
Free Software Foundation, either version 3 of the License, or 
(at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with this program. If not, see http://www.gnu.org/licenses.
"""
        elif whatToView == "Credits":
            data = """The icon of the project results from the combination of the work 
"donut chart", by Creative Stall and "Basketball", by samuel nudds, 
from The Noun Project. This work is licensed under the Creative 
Commons Attribution 3.0 United States License. To view a copy of
this license, visit http://creativecommons.org/licenses/by/3.0/us/
or send a letter to Creative Commons, PO Box 1866, Mountain View, 
CA 94042, USA.
"""
            
        frame = Frame(popup)
        txt = Label(frame, text=data)
        title = Label(frame, text=whatToView, font=("", 14, "bold"))
        
        Grid.columnconfigure(popup, 0, weight=1)
        Grid.columnconfigure(frame, 0, weight=1)
        frame.grid(ipadx=10, ipady=5, sticky=E+W+S+N)
        title.grid()
        txt.grid()

        
    window = Toplevel()
    # not resizable
    window.resizable(0,0)
    
    frame = Frame(window)
    
    try:
        img = PIL.Image.open('{}/icon.ico'.format(MY_PATH)).resize((100, 100))
        # make the photo printable by the Label widget
        img = PIL.ImageTk.PhotoImage(img)
        icon = Label(frame, image=img)
        # to avoid garbage-collection of the image
        icon.image = img
    except FileNotFoundError:
        icon = Label(frame, text='')
    
    name = Label(frame, text='Game-stats-manager', font=("", 14, "bold"))
    desc = Label(frame, text='A tool to collect and visualize team stats during a match',
                 font=("", 11, ""))
    version = Label(frame, text='Version {}'.format(VERSION))
    copyright = Label(frame, text='Copyright © {} {}'.format(YEARS, AUTHORS))
    contact = Label(frame, text='Contact : {}'.format(CONTACT))
    link = Label(frame, text="Visit the project page", fg="blue", cursor="hand2", 
                 font=("", 10, "underline"))
    link.bind("<Button-1>", browse)
    btnFrame = Frame(window)
    credits = Button(btnFrame, text='Credits', command=lambda: viewLicense("Credits"))
    license = Button(btnFrame, text='License', command=lambda: viewLicense("License"))
    
    Grid.columnconfigure(window, 0, weight=1)
    Grid.columnconfigure(btnFrame, 0, weight=1)
    Grid.columnconfigure(btnFrame, 1, weight=1)
    
    i = 0
    frame.grid(row=i, column=0, padx=10, pady=5)
    i += 1
    icon.grid(row=i, column=0)
    i += 1
    name.grid(row=i, column=0)
    i += 1
    desc.grid(row=i, column=0)
    i += 1
    version.grid(row=i, column=0)
    i += 1
    copyright.grid(row=i, column=0)
    i += 1
    contact.grid(row=i, column=0)
    i += 1
    link.grid(row=i, column=0)
    i += 1
    btnFrame.grid(row=i, column=0, padx=5, pady=5, sticky=E+W+S)
    credits.grid(row=0, column=0, sticky=E)
    license.grid(row=0, column=1, sticky=W)

    
    
##------ CLASSES ------##
class TkFS(tix.Tk):        
    def __init__(self):
        tix.Tk.__init__(self)
        self.fullscreen = IntVar()
        self.menu = None
        self.gframe = None
    
    def toogle_fullscreen(self, *event):
        """Toogle fullscreen mode, covering the OS's taskbar(s) and hidding the 
        window title bar. If an event is given as parameter, it first toogles
        the self.fullscreen attribute
        """
        if event:
            # Called by <F11>
            self.fullscreen.set(int(not self.fullscreen.get()))
        if self.fullscreen.get():
            self.attributes('-fullscreen', True)
        else:
            self.attributes('-fullscreen', False)

class chgHeaderWindow(Toplevel):
    """Window displayed when the "Edit > Categories" menu is called"""
    def __init__(self, game, root):
        Toplevel.__init__(self)
        self.title("Catégories")
        self.warning = Label(self, text="Attention : cette action va réinitialiser les scores.")
        self.text = Label(self, text="Vous pouvez ajoutez, modifier et supprimer des catégories")
        self.btn1 = Button(self, text="Annuler", command=self.destroy)
        self.btn2 = Button(self, text="OK", command=lambda game=game: self.ok(game))
        self.subFrame = Frame(self)
        self.warning.grid(row=0)
        self.text.grid(row=1)
        self.subFrame.grid(row=2)
        self.btn1.grid(row=3, sticky=S+W)
        self.btn2.grid(row=3, sticky=S+E)
    
    def ok(self, game):
        categories = []
        CatConfigField.fields.pop(0) # 'Players' field
        for r in CatConfigField.fields:
            cat = r.entry.get()
            dual = bool(r.chkvar.get())
            categories.append((cat, dual))
        kwargs = game.__dict__
        kwargs['categories'] = categories
        kwargs['team'] = game.team.get()
        kwargs['opponent'] = game.opponent.get()
        game.set_newgame(root, playerNames=[e.get() for e in root.gframe.entries], **kwargs)
        self.destroy()

class CatConfigField(Frame):
    fields = []
    def __init__(self, master, cat, dual, i):
        Frame.__init__(self, master)
        self.index = i
        self.entry = Entry(self)
        self.entry.insert(0, cat)
        if i == 0:
            self.entry.configure(state='readonly')
        self.addbtn = Button(self, text='Ajouter', command=lambda master=master, i=i+1: self.addfield(master, i))
        if i > 0: # Doesn't concern the 'Player' field
            self.rmbtn = Button(self, text='Supprimer', command=lambda master=master: self.rmfield(master))
            self.chkvar = IntVar()
            self.chkvar.set(int(dual))
            self.chkbtn = Checkbutton(self, text="dual ✓/✗", variable=self.chkvar)
        
        self.entry.grid(row=0, column=0)
        self.addbtn.grid(row=0, column=1)
        if i > 0:
            self.rmbtn.grid(row=0, column=2)
            self.chkbtn.grid(row=0, column=3)
        
        CatConfigField.fields.insert(i, self)
        self.display()
    
    def reset_index(self, master):
        for i,f in enumerate(CatConfigField.fields):
            f.index = i
            f.addbtn[COMMAND] = lambda master=master, i=i+1: self.addfield(master, i)
        self.display()
        
    def addfield(self, master, i):
        CatConfigField(master, '', False, i)
        self.reset_index(master)
    
    def rmfield(self, master):
        CatConfigField.fields.pop(self.index)
        self.reset_index(master)
        self.destroy()
        
    def display(self):
        for i,f in enumerate(CatConfigField.fields):
            f.grid_remove()
            f.grid(row=i, column=0, sticky=W)
            
class ScoreButton(Button):
    def __init__(self, master, game, r, c, fg=BLACK):
        Button.__init__(self, master, textvariable=game.score[r][c], fg=fg,
                        command=lambda r=r, c=c: self.add(game, r, c))
        self.subBtn = Button(master, text='-', fg=fg,
                                command=lambda r=r, c=c: self.sub(game, r, c))
    def add(self, game, r, c):
        """Add one to the clicked stat button"""
        if not game.freezed:
            current = game.score[r][c].get()
            game.score[r][c].set(current + 1)
    
    def sub(self, game, r, c):
        """Substracte one to the clicked stat button"""
        current = game.score[r][c].get()
        if not game.freezed and current != 0:
            game.score[r][c].set(current - 1)

class GameFrame(Frame):
    def __init__(self, master, game):
        Frame.__init__(self, master)
        self.playerEntries = self.gen_playerEntries(game)
        self.header = self.gen_header(game)
        self.scoreGrid = self.gen_scoreGrid(game)
        for r in range(game.nbPlayers+1):
            Grid.rowconfigure(self, r, weight=1)
        for c in range(game.h.nbCat+1):
            Grid.columnconfigure(self, c, weight=1)
                    
    def gen_header(self, game):
        self.labels = [Label(self, text=game.h.col[0], justify="center", relief=RAISED)]
        self.labels[0].grid(row=0, column=0, sticky=N+S+E+W)
        for c, cat in enumerate(game.h.cat):
            fg = foreground(cat)
            self.labels.append(Label(self, text=cat, justify="center", fg=fg, relief=RAISED))
            self.labels[-1].grid(row=0, column=c+1, sticky=N+S+E+W)
    
    def gen_playerEntries(self, game):
        self.entries = []
        for r, p in enumerate(game.players):
            self.entries.append(Entry(self, textvariable=p.name, justify="center"))
            self.entries[-1].grid(row=r+1, column=0, sticky=N+S+E+W)
            
    def gen_scoreGrid(self, game):
        self.btns = [[] for r in range(game.nbPlayers)]
        for c, cat in enumerate(game.h.cat):
            fg = foreground(cat)
            for r in range(game.nbPlayers):
                self.btns[r].append(ScoreButton(self, game, r, c, fg))
                self.btns[r][-1].grid(row=r+1, column=c+1, sticky=N+S+E+W)
                self.btns[r][-1].subBtn.grid(row=r+1, column=c+1, sticky=S+E)
    
    def regen_gameFrame(self, game):
        self.__init__(root, game)
        self.grid(row=1, sticky=N+S+E+W)
     

class FileMenu(Menubutton):
    def __init__(self, master, root, game):
        Menubutton.__init__(self, master, text="Fichier")
        self.menu = Menu(self, tearoff=0)
        self["menu"] = self.menu
        self.newmenu = Menu(self, tearoff=0)
        
        
        if not os.path.exists(SAVE_TEMP_PATH):
            os.mkdir(SAVE_TEMP_PATH)
            for sport in sports:
                with open(SAVE_TEMP_PATH + '/{}.gsm'.format(sport['name']), 'w+', encoding='utf-8') as f:
                    f.write('CATEGORIES,{}\n'.format(';'.join([str(tupl) for tupl in sport['categories']])))
                    f.write('TIME_PARTITIONS,{}\n'.format(sport['timeSplit']))
                    f.write('NB_PLAYERS,{}\n'.format(sport['nbPlayers']))
            
        path, dirs, files = next(os.walk(SAVE_TEMP_PATH))
        for filename in files:
            if filename.endswith('.gsm'):
                name = filename[:-4]
                self.newmenu.add_command(label=name, command=lambda root=root, game=game, name=name: load_game(root, game, 'template', name))
        
        self.newmenu.add_separator()
        self.newmenu.add_command(label="Ouvrir un modèle...", command=lambda root=root, game=game: load_game(root, game, 'template'))
        self.newmenu.add_separator()
        self.newmenu.add_command(label="Réinitialiser le jeu", command=game.reset_game)
        self.menu.add_cascade(label="Nouveau jeu", menu=self.newmenu)
        self.menu.add_command(label="Ouvrir un jeu...", command=lambda root=root, game=game: load_game(root, game, 'game'))
        self.menu.add_separator()
        
        self.menu.add_command(label="Sauvegarder le jeu sous...", command=lambda game=game: save(game, 'game'))
        self.menu.add_command(label="Sauvegarder les stats sous...", command=lambda game=game: save(game, 'stats'))
        self.menu.add_separator()
        
        self.templatemenu = Menu(self, tearoff=0)
        self.templatemenu.add_command(label="Sauvegarder le modèle actuel...", command=lambda game=game: save_template(root, game))
        self.templatemenu.add_command(label="Gérer...", command=lambda root=root, game=game: ManageTemplates(root, game))
        self.menu.add_cascade(label="Modèles", menu=self.templatemenu)
        
        self.menu.add_command(label="Générer les stats", command=lambda root=root, game=game: show_stats(root, game))
        self.menu.add_separator()
        
        self.menu.add_command(label="Quitter", command=lambda root=root, game=game: safeExit(root, game))

class EditMenu(Menubutton):
    def __init__(self, master, root, game, frame):
        Menubutton.__init__(self, master, text="Édition")
        self.menu = Menu(self, tearoff=0)
        self["menu"] = self.menu
        self.menu.add_command(label="Catégories", command=lambda game=game, root=root: game.chgHeader(root))
        self.menu.add_command(label="Nombre de joueurs", command=lambda root=root, game=game: game.chgNbPlayers(root))
        self.menu.add_command(label="Nombre de périodes", command=lambda root=root, game=game: game.chgNbTs(root))

class DisplayMenu(Menubutton):
    def __init__(self, master, root):
        Menubutton.__init__(self, master, text="Affichage")
        self.menu = Menu(self, tearoff=0)
        self["menu"] = self.menu
        self.menu.add_checkbutton(label="Plein écran", variable=root.fullscreen, command=root.toogle_fullscreen, accelerator="F11")
        
class TeamEntry(tix.LabelEntry):
    def __init__(self, master, *team):
        tix.LabelEntry.__init__(self, master, label=team[0], labelside=LEFT)
        self.entry["textvariable"] = team[1]
        self.entry["width"] = 20
        
class HelpMenu(Menubutton):
    def __init__(self, master):
        Menubutton.__init__(self, master, text="Aide")
        self.menu = Menu(self, tearoff=0)
        self["menu"] = self.menu
        self.menu.add_command(label="Documentation", command=browse)
        self.menu.add_command(label="À propos", command=about)

class TsFrame(Frame):
    def __init__(self, master, game):
        Frame.__init__(self, master, bd=2, relief=SUNKEN)
        if game.timeSplit > 1:
            text = tslabel(game)
            Label(self, text=text).grid(row=0, column=0)
            for i in range(game.timeSplit):
                rb = Radiobutton(self, text=str(i+1), variable=game.currentTs, value=i, 
                                command=lambda game=game, i=i: game.chgTs(i))
                rb.grid(row=0, column=i+1)
        self.EOMbtn = Button(self, text='Fin du Match', 
               command=lambda game=game: game.chgTs(game.timeSplit))
        self.EOMbtn.grid(row=0, column=game.timeSplit+1)
        
class MainMenu(Frame):
    """Creates the top menubar of the root windows"""
    def __init__(self, root, game):
        Frame.__init__(self, root, relief=RAISED, bd=1)
        self.filemenu = FileMenu(self, root, game)        
        self.editmenu = EditMenu(self, root, game, root.gframe)
        self.displaymenu = DisplayMenu(self, root)
        self.teamEntry = TeamEntry(self, 'Équipe : ', game.team)
        self.opponentEntry = TeamEntry(self, 'Adversaire : ', game.opponent)
        self.helpmenu = HelpMenu(self)
        self.tsframe = TsFrame(self, game)
        
        self.filemenu.grid(row=0, column=0)
        self.editmenu.grid(row=0, column=1)
        self.displaymenu.grid(row=0, column=2)
        self.tsframe.grid(row=0, column=3, padx=5, ipadx=1)
        self.teamEntry.grid(row=0, column=4, padx=5, sticky=E)
        self.opponentEntry.grid(row=0, column=5, padx=5, sticky=W)
        self.helpmenu.grid(row=0, column=6, sticky=E)
        self.grid(row=0, column=0, sticky=N+E+W)
        for i in (4,5):
            self.grid_columnconfigure(i, minsize=100, weight=1)
    
    def regen(self, root, game):
        self.grid_remove()
        self.__init__(root, game)
        self.grid(row=0, sticky=N+S+E+W)

class MenuStats(Menu):
    def __init__(self, statsWin, game):
        Menu.__init__(self, statsWin)
        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label="Sauvegarder les stats", command=lambda game=game: save(game, 'stats'))
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quitter", command=statsWin.destroy)
        self.add_cascade(label="Fichier", menu=self.filemenu)

#################  MAIN  ###################
if __name__ == '__main__':
    # Generating the main objects
    root = TkFS()
    game = Game(root)
    root.gframe = GameFrame(root, game)
    root.menu = MainMenu(root, game)
    
    # Displaying the root menu and the score interface
    root.menu.grid(row=0, sticky=N+S+E+W)
    root.gframe.grid(row=1, sticky=N+S+E+W)
    
    # Configuring the root window
    root.title("Game Stats Manager")
    Grid.rowconfigure(root, 1, weight=1)
    Grid.columnconfigure(root, 0, weight=1)
    root.protocol("WM_DELETE_WINDOW", lambda root=root, game=game: safeExit(root, game))
    root.bind("<F11>", root.toogle_fullscreen)
    root.focus_force()
    
    # Creating or loading the config file
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf8') as f:
            SAVE_TEMP_PATH = f.readline().strip()
            SAVE_GAME_PATH = f.readline().strip()
            SAVE_STATS_PATH = f.readline().strip()
            last_template = f.readline().strip()
        
        if last_template:
            try:
                load_game(root, game, 'template', last_template)
            except:
                game = Game(root)
                regen_interface(root, game)
    
    else:
        with open(CONFIG_PATH, 'w+', encoding='utf8') as f:
            f.write(SAVE_TEMP_PATH + '\n')
            f.write(SAVE_GAME_PATH + '\n')
            f.write(SAVE_STATS_PATH + '\n')
            f.write('')
    
    root.mainloop()

    

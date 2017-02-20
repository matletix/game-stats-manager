# HOW TO USE

Game-stats-manager lets you record scores for a specific activity that you define.

The main interface is composed of a toolbar and a table, with rows

representing players and columns representing categories.

---

## The Score Grid

![](/assets/main.png)

It is the table composed of buttons. On each button is displayed a score relative to the player and the categorie it intersects. For each player, you can increment the counter corresponding to a category by

clicking on it. If you increase a counter by accident, it is possible to

decrease it by clicking on the tiny minus sign on the bottom right corner of the case.

---

## The Toolbar

![](/assets/toolbar.png)

The toolbar is the bar on the top of the main window. It is composed of

the File, Edit, Display and Help menus and of the Period, Team and

Opponent fields.

## 

## The Period field

![](/assets/periods.png)

You can divide the record of your stats in several parts. In

the period field, corresponding to the rectangle right to the Display

menu, the current period being recorded is selected with a radio button.

For a soccer match, traditionnally divided into two halves, you start

your game with the first half selected. At the half time, you select the

second half : the current grid of scores will be stored in the first

part of the game, and the grid will reinitialize to record the second

part. When the match finally ends, click on the "End of Match" button.

It will have for effect to : freeze the score grid, making it impossible

to further modify; record the second half, and calculate the total

period statistics, that next can be displayed.

## The Team and Opponent fields

![](/assets/team.png)

You can provide an optional name for the team you are recording the scores of and its opponent. They will be recorded when you save the game or the stats.

## The Display menu

![](/assets/display.png)

From this menu you can access a command to toggle the window to fullscreen view

## The Edit Menu

![](/assets/edit.png)

It allow to edit three part of the game.

### &gt; Categories

![](/assets/columns.png)

From this window it is possible to add, edit and remove columns. Click on the Add button in front of a category to insert one just below it. Just edit the name of a column to change it. For every category, it is possible to make it dual. When a category is set dual, it will appears twice in the score grid : one in green with a 'succeed' tick, the other in red with a 'failed' tick. When generating statistics, the percentages of succeed and failed will be showned for each dual category.

### &gt; Number of players

Change the number of players that are monitored. As a consequence, it resets the game. It is possible to add up to 99 players.

### &gt; Number of time divisions

Change the number of periods taken in account in the Period field. As a consequence, it resets the game. It is possible to add up to 20 periods.

## The File menu

### &gt; New game

![](/assets/new-game.png)

Starts a new game by either reseting the current game or loading a predefined game template which is a template with predefined number of periods and players, and predefined categories.

### &gt; Open a game

Load a game previously saved with the 'Save game' option of the File menu. It is a CSV file.

### &gt; Save game

Save the current game states to a CSV file in order to continue it later by reloading the game with the 'Open a game' option.

### &gt; Save stats

Save the game statistics to a CSV file that can be opened and analysed by a spreadsheet.

### &gt; Template

![](/assets/templates-menu.png)

The 'Save the current game template' option saves the current game configuration \(number of periods, number of players and categories\) in the 'template' folder, making it accessible through the 'New game' option.

The 'Manage' option allows to visualize the different saved templates, to remove and to rename them. The thumbnail preview is taken when saving the template via the 'Save the current game template' option.

![](/assets/templates.png)

### &gt; Generate Stats

![](/assets/stats.png)

Open a window with the game statistics, one tab by period, plus one tab for the full time stats


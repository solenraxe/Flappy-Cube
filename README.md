# Flappy-Cube
I made this game for an arcade machine as part of the coding club at my school, it was meant to be a normal flappy bird game but that'd be boring...

The name's Flappy Cube because it was composed of rectangles during its early stages, thus earning the name "Flappy Cube" from my friends.

Please message me if you have any suggestions, bug reports or inquiries, or any reason really, I am very much opened to discussion.

The game runs on Python 13.3.3 using Pygame.

Additionally to the Flappy Bird gameplay, this game boasts a few more features such as :
- Skins : 6 different skins, with 7 color variations each.
- Multiplayer, up to 2 players, you could push it to 4 by changing the script.
- Stat points you can allocate to either boost your jump power, gravity or inertia.
- Difficulties : Easy, Normal and Hard, Normal being the default one.
- A local leaderboard (meant for the arcade machine).
- 3 different abilities you can use to give yourself an advantage when playing!

As this is meant to be played on an arcade machine, the keybinds are awkward, I'll list them at the bottom, I might also change them in the future.

Notes :
- I have no idea what I'm doing, this is my first time making a script that actually requires more than the variables in the script itself and as such I am not sure if it'll run on any other interpreter than VSCode, however, it should work if you open the folder in VSCode by clicking File > Open Folder.
- If you want to modify the maximum number of players, the variable is named max_players.
- Keybinds can be modified by searching for : 
"if event.type == pygame.KEYDOWN:"
and modifying the values accordingly.
- You also have acces to a script named change_color.py that I used to create the color variants for the skins. It works by putting the green version of an image named InsertSkinNameHereGreen in a folder named InsertSkinNameHere inside the assets folder then changing "Dino" with the Skin Name when calling the function.
- I am aware of a bug where you can press both Space and Up to jump twice the height with P1, however I do not want to compromise on one of the keys nor do I want to make a system to fix it, it's meant for an arcade machine after all.

Default keybinds are as follow :
- Space : Jump (Player 1)
- Up, Down, Right and Left arrows (in-game) : Jump (P1, P2, P3 or P4 respectively).
- Esc (in-game) : Pause/Resume the game
- Z/S (in-game) : Use ability (P1 or P2 respectively).
- Tab (menu) : Switch between stats/settings when changing them, also switches between players when editing Abilities, Skins or Colors or letters in H.S. Menu
- A (High score menu) : Confirm letter choice.
- Up & Down arrows (menu) : Should be pretty instinctive/written.
- Left & Right arrows (menu) : Switch between menus.

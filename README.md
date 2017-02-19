# Plundering Pirates of Pim!

*The land of Pim is failing. Oppresed by the Great Vilnius Empire, striped of its resources and history, the people look for a saviour. In to this void step the Pirates of Pim, privateers who seek to throw off the yolk of oppression and free their people. As the Pirate's successes grow, the Empire sends Arch Duke Gediminas to crush them and restore order to Pim.*

## Resources

- Framework: [Python Arcade](https://pythonhosted.org/arcade/index.html "Python Arcade")
- Base Assets: [Pirate Pack](http://kenney.nl/assets/pirate-pack "Pirate Pack")
- Support Assets: None
- Genre: Shoot 'em Up

## Tools

- [PyCharm](https://www.jetbrains.com/pycharm/ "PyCharm")
- Project Management: [Plundering Pirates of Pim Trello](https://trello.com/b/KyhPjpRT/plundering-pirates-of-pim 'Plundering Pirates of Pim Trello')
- [GitHub](https://github.com/froomzy/game-prototype-one "GitHub")

## Gameplay and Design
**Goal:** *Traverse the level, sinking enemy ships, destroying their forts, avoiding running aground, all the while styaing alive and plundering loot.*

The player will have one **life**. They make take several hits, which cost them their health resource, **crew**. They have a limit on **crew**, which can be replenished by **pickups**. They may also gain and lose extra **crew** slots via different kinds of **pickups**.

The players ship starts with two **cannons** which fire at 45° angles to either side of the ship. The **cannons** may be improved via **pickups** to fire faster, fire more shots, do more damage, or have more range. The players ship may also be upgraded with an additional **cannon** that fires directly forward.

The player's primary goal is to get to get to the end of the level and defeat the **boss**. Along the way they will have opportunites to score points, known as **doubloons**, by sinking enemy ships and picking up their cargo. When a player finishes a game, either by defeating the **boss** or dying, then their score may be recorded in the **top scores** *if* they are one of the top 10 highest scores. If the new score ties with an existing score, then the new score ranks lower then the old.

Enemy ships will come in waves known as **convoies**. Each **convoy** will contain 1 or more ships, and will follow a pattern. Each ship will drop **cargo**: loot that they player may collect for **doubloons**. As well as points the **cargo** may contain **pickups** that will improve the players ship. If the player destroys all ships in a **convoy** then they will recieve extra **cargo**.

At several points throughout the level the player will encounter **fortresses**. These **fortresses** will consist of some walls and towers with **cannons**. The player can destroy these just as they do **convoys**. If the player destroys all a **fortresses** **cannons** then they will recieve extra **cargo**.

The **boss** of the level is Arch Duke Gediminas. He will be encountered aboard his flagship, *Gangut*. There will be several phases to the **boss** fight, but these still need to be designed. After each phase is completed, the player will have a short respite before the next begins. More to be decided about how this will work.
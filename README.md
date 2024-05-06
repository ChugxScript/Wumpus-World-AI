# Wumpus-World-AI

Wumpus World is a classic problem in artificial intelligence used to demonstrate reasoning under uncertainty. In this environment, an agent navigates a grid-based world filled with hazards like bottomless pits and a fearsome Wumpus. The agent's objective is to find gold and return to safety while avoiding dangers. The agent uses logic and inference to deduce the locations of hazards based on sensory input, making it a classic problem for studying search algorithms, logical reasoning, and planning in AI.

_This repository serves as Machine Problem 4 in subject CS322-M_-_CS321L-M - Artificial Intelligence_

## USAGE

- git clone `https://github.com/ChugxScript/Wumpus-World-AI.git`
- git install `requirements.txt`
- run `main.py`

## RULES

- Stench: Rooms adjacent to the Wumpus emit a stench.
- Breeze: Rooms adjacent to pits have a breeze.
- Glitter: Rooms with gold contain glitter.
- Wumpus: The agent can kill the Wumpus if facing it, emitting a scream audible throughout the cave

## PEAS description

- +1000 points for exiting the cave with gold.
- -1000 points for being eaten by the Wumpus or falling into a pit.
- -1 point for each action, and -10 points for using an skill

## ENVIRONMENT

- User can choose in game mode whether user want to play as an AI or play by the user
- User can choose what world size they want from 4x4 to 10x10
- Agent starts at [0, 0], facing right because why not.
- Wumpus and gold are randomly placed.
- Each room has a x probability of containing a pit, except [0, 0] depending on the world size.
- The number of Wumpus and gold generate base on the world size.

## ACTUATORS

- Turn left, right, above, and below
- Grab gold
- Shoot skill
- Climb

## SENSORS

- Perceive
  - `Stench` if cell is adjacent to wumpus
  - `Breeze` if cell is adjacent to wumpus
  - `Glitter` if cell is adjacent to wumpus
  - `Bump` if move to wall
- Agent perceives the scream if Wumpus is shot

## PREPOSITION

- Pij: Pit in room [i, j].
- Bij: Agent perceives breeze in [i, j].
- Wij: Wumpus in [i, j].
- Sij: Agent perceives stench in [i, j].
- Vij: Room [i, j] visited.
- Gij: Gold (and glitter) in [i, j].

```
for (nrow, ncol), stats in self.adjacent():
    if "S" in actual_components:
        if "W?" in self.kb[nrow][ncol][self.W]:
            if "V" not in self.kb[nrow][ncol]:
                self.kb[nrow][ncol][self.W] = "W"
                if self.skill != 0:
                    print(f"\n>> wumpus killed in self.kb[{nrow}][{ncol}]")
                    print(f">> self.skill: {self.skill}")
                    self.skill -= 1
                    self.load_skill_gold_()
                    self.update_perceive('enemy', (nrow, ncol))
        elif "~W" not in self.kb[nrow][ncol][self.W]:
            self.kb[nrow][ncol][self.W] = "W?"
    else:
        self.kb[nrow][ncol][self.W] = "~W"

    if "B" in actual_components:
        if "P?" in self.kb[nrow][ncol][self.P]:
            if "V" not in self.kb[nrow][ncol]:
                self.kb[nrow][ncol][self.P] = "P"
        elif "~P" not in self.kb[nrow][ncol][self.P]:
            self.kb[nrow][ncol][self.P] = "P?"
    else:
        self.kb[nrow][ncol][self.P] = "~P"
```

## EXPLORATION

- initial world, where it checks the current cell status

  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/f5cf42a3-3e43-482c-ad32-02d8f69fae3c)

- only in the safe and unvisitted cells that our agent can move but it can backtrack if there are no other cells and then move again to unvisitted safe cells. 
In this scenario, the agent moves to [1, 0] and perceive `Stench` so it mark the adjacent cells as `W?` saying that theres mayba a wumpus then go back and check safe cells

  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/1e9e1172-cf30-407b-9407-b45003152c36)

- in this scenario, our agent detects `Stench` again and in the cell [1, 1] is `W?` so therefore that cell is wumpus and the other cell is not

  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/fcb4479a-0efb-4099-b7d8-e60ce26d1ca3)


## SCREENSHOTS

- Main page
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/6ad3dc4e-718f-4bd7-b2e9-d6031a069b31)

- Select Game Mode
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/6babc040-c930-4510-a748-9572802ee4e5)

- Select World Size
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/eb8f555d-e3c1-4126-a4d5-c0e202cfc97d)

  - 4x4
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/b08df94d-1c0e-4d46-8f14-9169cd783615)
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/0e21fadc-f11c-421b-b35d-5e82961e986f)


  - 6x6
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/9458065e-3af4-458b-89c0-b2650d5123de)
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/b9625dd1-12cb-477e-8a1e-c90b6255f6d9)

  - 8x8
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/17496ae2-a4f1-451f-b5f9-e9eaff1a0be3)
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/aa2e15da-4b56-41c1-a8a2-9cd3f405a81c)

  - 10x10
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/62135619-789b-4c21-98ad-fb7f5c40e089)
  ![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/6997313a-8707-48ab-a092-95c5e0d3722f)


- Controls
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/8a0a5230-373e-4445-b0e4-3e464f836ee8)

- Killed wumpus
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/43b1a423-95c7-4303-a990-f955eb776208)

- Win
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/7383f88d-4739-4757-a22f-614ade7ad378)

- Lose
![image](https://github.com/ChugxScript/Wumpus-World-AI/assets/101156843/248e7f08-09d9-4e33-8b95-131291a82040)


## ACKNOWLEDGMENT 

I would like to thank these guys helping me out to finish this project. 
Their repo serve as a guide and inspiration in the game logic <3
- @sudohumberto - https://github.com/sudohumberto/wumpus-world
- @thiagodnf - https://github.com/thiagodnf/wumpus-world-simulator

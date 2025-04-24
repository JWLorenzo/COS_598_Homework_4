# COS_598_Homework_4

- Name: Jacob Lorenzo
- Date: 4/11/25
- Assignment: COS_598_Homework_4
- Instructor: Dr. Hutchinson

# General Overview

The AI I’ve developed coordinates offensive and defensive unit movement, builds units in response to enemy composition, and uses a terrain-weighted A* pathfinding algorithm enhanced with influence-based goal weighting. The AI is shared by both factions, and the core logic for movement and production is contained within ai.py.

## How-To
- Run the main.py file from the repository root.
- Ex: ```py main.py```

# Use of Terrain

Terrain affects multiple aspects of gameplay. Each tile’s terrain type provides attack and defense modifiers, influencing combat outcomes. These same tiles also impose movement penalties, which factor into A* pathfinding costs. In practice, this causes units to avoid high-cost terrain like mountains and favors more strategic navigation through the map.

# Pathfinding and Movement

To reduce overhead, I implemented A* with precomputed cell neighbors. In early tests, units formed tight “conga lines” due to overly deterministic targeting. To address this, I introduced stochasticity into goal selection by weighting tiles based on influence scores. These values decay outward from cities and units, encouraging a wider spread around objectives and resulting in more swarm-like movement.

Influence values are cached to reduce redundant computation. Each unit maintains a movement queue that is recalculated only when necessary. If a path is blocked, the unit clears its queue and selects a new goal.

# Target Identification and Threat Evaluation

Target selection is guided by a weighted tile list that incorporates influence scores, offensive/defensive values, and terrain bonuses. The game map tracks threat zones by faction, which the AI uses to prioritize movement. Units switch between offensive and defensive behavior depending on whether they are outnumbered. Defensive actions focus on threats near high-value areas such as cities.

# Unit Production

Unit builds are determined stochastically based on the enemy’s current composition. The opponent’s unit counts are used as inverse weights; if the Red faction has many Rock units, for example, the Blue faction is more likely to build Paper. This system allows the AI to dynamically counter the opposing side’s forces over time.

# Performance Optimizations
To reduce the computational cost of running A* for many units, I implemented several optimizations:
- Pathfinding cache: Stores previously computed paths.
- Precomputed neighbors: Avoids redundant neighbor lookups during pathfinding.
- Unit upkeep system: Each unit reduces income by 1, helping cap unit counts and balance gameplay.
These changes significantly improved performance during high unit-count scenarios. While some lag remains, it is substantially reduced. Future improvements could include multithreading to further boost performance.

# Game Optimizations
As a personal challenge and inspired by my peers’ work, I transitioned the game to a hex-based map system. This required reworking offset logic, UI rendering, and display scaling for fullscreen mode. I also added new UI elements like unit counts and improved the legibility of unit visuals to support gameplay clarity.

# Future Work
Going forward, I’d like to explore a swarm-based model where one unit computes a path and nearby units follow it to reduce overall pathfinding overhead. I also see potential in using multithreading for influence propagation and pathfinding to improve frame stability.

# Extra Credit
I fully converted the game from a square grid to a hex-based system, requiring significant changes to movement logic, UI rendering, and game interaction. This overhaul supports a deeper level of strategy and visual clarity, and is used directly by the AI for movement and evaluation.

# Sources:
- https://www.redblobgames.com/grids/hexagons/
- https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar
- https://www.redblobgames.com/grids/hexagons/#neighbors 
- https://github.com/BryantCabrera/Settlers-of-Catan

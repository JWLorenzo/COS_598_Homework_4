# COS_598_Homework_4

# Notes:

- Towers generate units based on surrounding units

- Evaluation of movement "worthness" based on distance to a given unit and the distance to a given tower.

- Economy? 
    - The more of a unit that exists, the cheaper they are

- Ideas: 

    - Builders
        - Roadmakers that create optimal paths from a given place to another place so towers can manuever terrain with ease.
    - Medics
        - Heal other units
    - Mages
        - Grant other units flight so they can move on other unit tiles and ignore terrain 


Simplistic plan of implementation:


Three different categories of influence:
- Victory
    - Relative to the terrain, the cities will have a victory influence that will be the driving factor for offenses pathfinding.
- Offense
    - The evaluation of the influence of the units marked as offense. 
- Defense
    - The evaluation of the influence of the units marked as defense.

- Offense and Defense influence are affected by terrain bonuses that will buff / debuff certain actions. 

We divvy up the units between two different categories:

Offense:
- Evaluates the map for the current city with the greatest victory influence, then modifies that evaluation based on the defense influence.  

Defense:
- Evaluates the current defense influence around cities and how far these cities are from the greatest offense influence. 
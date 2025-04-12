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

# Sources/Elaboration (mini-writeup?):
- Since I'm using a hex-based system, I found a blog online about implementation of hex-based geometry in code. https://www.redblobgames.com/grids/hexagons/

- I used this source because no doubt would this have been a waaay easier assignment if I decided to use grid based, but I saw the insanely cool work that Sophie(?) did with the isometric view and it inspired me to do something cool for this one as well. It also gave me a good opportunity to gain a greater understanding of pygame because I haven't actually used it all that much, so it was a learning experience into how to optimize calculations for video games because I noticed that the influence example you showed us in class got waaay slower when I tooled around with it by printing out each iteration. It progressively got slower, so I realized that iterating over every tile to calculate influence wasn't going to cut it. To optimize it, I decided to make an influence function that notes a given criteria.

- I also used this link because they had an implementation of A* and a path reconstructor. https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar

    - I presume using these / this source isn't problematic since they're just textbook algorithms we've used before. 

- I got the images from here: https://github.com/BryantCabrera/Settlers-of-Catan

- To calculate influence, I based my algorithm off their algorithm for distance calculations for a double width tile format and then modified it to iterate over ranges. I used a double width coordinate system because it seemed like it would be the easies to implement when translating from a grid-based to hex-based. 

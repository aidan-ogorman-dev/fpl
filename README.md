# Fantasy Premier League Python Library

## Heatmap
The heatmap library takes a set of parameters and generates a "fixture difficulty" matrix using Seaborn's heatmap plot functionality. Fixture difficulty is not typically shown as a matrix on the FPL website so this chart provides us with some additional insights:
* it shows which teams have similar difficulties for the next N weeks, which indicates that we may want to transfer in or out players from both teams
* if teams are "alternating" in terms of fixture difficulty in successive weeks, we can buy in a player from each team in the same position and rotate them

```
aidanogorman: ~ $ python3
Python 3.8.5 (default, Jul 28 2020, 12:59:40) 
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from fpl import heatmap as hm
>>> hm.plotHeatmap(1, 10)
```
![FPL Heatmap Visualization](https://github.com/aidan-ogorman-dev/fpl/blob/main/images/fpl_heatmap.png)

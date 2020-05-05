# The Restaurant Game

A group of delegates attends a long conference in an unfamiliar town.
Each night they have to find somewhere to dine.
There is a large choice of restaurants, each of which offers a large variety of meals.
The problem the group faces is to find the best restaurant, that is the restaurant where the maximum number of delegates would enjoy dining.
Even a parallel exhaustive search through the restaurant and meal combinations would take too long to accomplish.
To solve the problem delegates decide to employ a Stochastic Diffusion Search.

Each delegate acts as an agent maintaining a hypothesis identifying the best restaurant in town.
Each night each delegate tests his hypothesis by dining there and randomly selecting one of the meals on offer.
The next morning at breakfast every delegate who did not enjoy his meal the previous night, asks one randomly selected colleague to share his dinner impressions.
If the experience was good, he also adopts this restaurant as his choice.
Otherwise he simply selects another restaurant at random from those listed in "Yellow Pages".

Using this strategy it is found that very rapidly [a] significant number of delegates congregate around the best restaurant in town.

# Discussion

The process of the restaurant game has a number of notable features.
Within minimal centralised control the group of delegates acts together to solve a problem that could not be quickly solved by an individual.
The delegates will efficiently move to the next best restaurant if the current one has a significant drop in standards or closes down entirely.
The restaurants, the menus, or the individual meals need to be directly comparable, all that is required is for each agent to decide for themself whether their experience was good.
Delegates will find themselves enjoying many evenings in a relatively high quality restaurant long before all of the meals in all of the restaurants in town could have been evaluated.

This analogy has been criticised on the grounds that delegates are likely to have differing dining preferences and hence it is possible for a delegate to locate a restaurant in which they enjoy all of the meals on offer, but which is unsatisfying to all other delegates.
In the case where only one delegate, or a small proportion of the group, remains permanently at such a restaurant the rest of the group will proceed largely as usual and so the majority will still converge on the best restaurant.
Taken to the extreme, however, all agents may find themselves dining alone, even when there exists a single superior restaurant which would satisfy the largest portion of the delegates.
This superior restaurant would never be located as all delegates are satisfied with the meals at their current restaurant, and hence never select a new restaurant.
This critique led to the development of [The Mining Game](mining-game.md), which depends on the less subjective notion of locating gold rather than dining preferences.

# References

K. De Meyer, J. M. Bishop, and S. J. Nasuto. Stochastic diffusion: using recruitment for search. *Evolvability and interaction: evolutionary substrates of communication, signalling, and perception in the dynamics of social complexity (ed. P. McOwan, K. Dautenhahn & CL Nehaniv)* Technical Report, 393:60--65, 2003. [BibTeX](http://aomartin.ddns.net/sds-repository/conference_proceedings_bib.html#de2003stochastic), [PDF](http://aomartin.ddns.net/sds-repository/downloads/de2003stochastic.pdf)

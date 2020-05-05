# The Mining Game

A group of friends (miners) learn that there is gold to be found on the hills of a mountain range but have no information regarding its distribution.
On their maps the mountain range is divided into a set of discrete hills and each hill contains a discrete set of seams to mine.
Over time, on any day the probability of finding gold at a seam is proportional to its net wealth.

To maximise their collective wealth, the miners need to identify the hill with the richest seams of gold so that the maximum number of miners can dig there (this information is not available a-priori).
In order to solve this problem, the miners decide to employ a simple Stochastic Diffusion Search.

* At the start of the mining process each miner is randomly allocated a hill to mine (his hill hypothesis, *h*).
* Every day each miner is allocated a randomly selected seam on his hill to mine.
* At the end of each day, the probability that a miner is happy is proportional to the amount of gold he has found.
* At the end of the day the miners congregate and over the evening each miner who is unhappy selects another miner at random to talk to.
If the chosen miner is happy, he happily tells his colleague the identity of the hill he is mining (that is, he communicates his hill hypothesis, *h*, which thus both now maintain).
Conversely, if the chosen miner is unhappy he says nothing and the original miner is once more reduced to selecting a new hypothesis - identifying the hill he is to mine the next day - at random.

In the context of SDS, agents take the role of miners; active agents being "happy miners", inactive agents being "unhappy miners" and the agent's hypothesis being the miner's "hill-hypothesis".
It can be shown that this process is isomorphic to SDS, and thus that the miners will naturally self-organise and rapidly congregate over hill(s) on the mountain range with a high concentration of gold.

# Discussion
The happiness of the miners can be measured probabilistically, or represented with an absolute boolean value, so long as each miner is either happy or unhappy by the end of each day.
Furthermore, if the gold is modelled as a finite resource, reducing over time, then the search is sufficiently adaptive that miners change where they congregate as the location with the most gold changes.

Though "happy" is a term that is similarly subjective as one's dining preferences, in this case it is used in an objective sense. All miners share an identical process whereby the amount of gold they locate on a single day defines a probability that the miner will declare themselves "happy" at the end of the day when miners congregate to potentially share the identity of the hills they are mining.} 

# References

M. M. al-Rifaie, J. M. Bishop, and T. Blackwell. Information sharing impact of Stochastic Diffusion Search on differential evolution algorithm. Memetic Computing, 4(4):327--338, 2012.  [BibTeX](http://aomartin.ddns.net/sds-repository/journal_publications_bib.html#al2012information), [PDF](http://aomartin.ddns.net/sds-repository/downloads/al2012information.pdf), [HTML](http://link.springer.com/article/10.1007/s12293-012-0094-y/fulltext.html).

from setuptools import setup

setup(
    name="sds",
    version="2.0",
    packages=["sds"],
    description="Stochastic Diffusion Search",
    keywords=["swarm", "artificial", "intelligence", "search"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    url="http://www.aomartin.co.uk/sds-library/",
    author="Andrew Owen Martin",
    author_email="a.martin@gold.ac.uk",
    long_description="""\
A library which implements the main variants of Stochastic Diffusion
Search (SDS), and provides a convenient front end.

Stochastic Diffusion Search (SDS) is a generic population-based search
method. SDS agents perform cheap, partial evaluations of a hypothesis (a
candidate solution to the search problem). They then share information
about hypotheses (diffusion of information) through direct one-to-one
communication. As a result of the diffusion mechanism, high-quality
solutions can be identified from clusters of agents with the same
hypothesis.

This is a library used during the writing of my PhD thesis, I will
publish full documentation and host the code on GitHub once the design
has settled down and I have submitted my thesis. Until then, feel free
to email me.

SDS has a Scholarpedia page:
http://www.scholarpedia.org/article/Stochastic_diffusion_search

A list of papers written on SDS can be found in the Stochastic Diffusion
Search paper repository, maintained by the author of this module:
http://aomartin.ddns.net/sds-repository/publications.html
""",
)

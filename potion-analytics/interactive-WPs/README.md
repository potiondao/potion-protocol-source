<!-- PROJECT SHIELDS -->

[![Potion][potion-shield]][potion-url]
[![Twitter][twitter-potion-shield]][twitter-potion-url]
[![Medium][medium-shield]][medium-url]
[![in][linkedin-shield]][linkedin-url]
[![Chat][discord-shield]][Discord Community]
<!--[![Apache 2.0 License][license-shield]][license-url] -->
<!--[![Python Versions][versions-shield]][versions-url] -->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/potion-labs/interactive-WPs">
    <img src="media/potion_logo.jpg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Kelly Pricing White Papers</h3>

  <p align="center">
    An awesome Interactive White Papers to dive into Option Pricing via Kelly Criteria
    <br />
    Explore the apps:
    <br />
    <br />
    <a href="https://kelly-single-instrument.herokuapp.com/">One Instrument Pricing</a>
    ·
    <a href="https://kelly-curve-designer.herokuapp.com/">Custom Pricing</a>
    ·
    <a href="https://kelly-input-generation.herokuapp.com/">Input Generation</a>
    ·
    <a href="https://kelly-vs-black-scholes.herokuapp.com/">Black-Scholes vs Kelly</a>
    ·
    <a href="https://kelly-portfolio-backtest.herokuapp.com/">Portfolio Backtest</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#installation-with-poetry">Installation with Poetry (Preferred)</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    
  </ol>
</details>

## Overview

[Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion) allows us to find optimal Premiums, which [Put or Call option](https://www.investopedia.com/terms/o/option.asp) seller is going to charge Put option Buyer. <br />
This repo has a number of tools to do Options Pricing via Kelly Criteria. <br />
There is a Monte Carlo backtester embedded, so we able to verify/asess how reasonable this pricing is. All the backtest results are shown from the perspective of the Option Seller.<br />
The easiest way to explore all the functionality is to visit the interactive web apps (links are in the README header). <br />
All the source code for the apps is in the [/src](https://github.com/potion-labs/interactive-WPs/tree/main/src) root. <br />
[/src/notebooks](https://github.com/potion-labs/interactive-WPs/tree/main/src/notebooks) holds some drafts/experiments of the apps. <br />
[/src/lib](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib) has the core code base with all the main calculations, which are extensively used in apps. This part is gonna be pip installable later on. <br />

## Installation

1) Install python3

2) git clone this repo

3) cd to repo

4) Optional: Add hook to automatically clear Jupyter Cells output before commit https://medium.com/somosfit/version-control-on-jupyter-notebooks-6b67a0cf12a3
.git/hooks/pre-commit file content:
```
#!/bin/sh

jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace src/notebooks/*.ipynb

git add src/\*.ipynb
```

5) to create a virtual enviroment run: `python3 -m venv env`

6) activate the virtual enviroment: (use this on subsequent launches to start the repo)
    * On mac / linux: `source env/bin/activate`
    * On windows: `source env/Scripts/activate`

7) Install required libraries: `pip3 install -r requirements.txt` or `pip3 install -r requirements_lock.txt` to have the same dependencies

8) Run one of the apps: streamlit run src/streamlit_app_single_instrument.py

P.S. pip install support is coming.

## Installation with Poetry

- do first four steps form the Installation section
- install Poetry with Python3 (OS specific): https://python-poetry.org/docs/#installation
- optional: if you'd like to have virtualenv folder in the project: `poetry config --local virtualenvs.in-project true`
- create virtualenv based on pyproject.toml files: `poetry env use 3.8` 
- install dependencies: `poetry install`
- activate your environment: `poetry shell`
- Run one of the apps: streamlit run src/streamlit_app_single_instrument.py

## Features

- Call and Put options support
- Heavy utilization of [Numpy](https://numpy.org/), [Pandas](https://pandas.pydata.org/) based calculations, which assures reasonably fast performance even for more than 10K Monte Carlo Paths. 
- Fully empirical calculations based on sample Prices data of the instrument of your choice.
- Black-Scholes pricing support.
- Comparison of the Black-Scholes vs Kelly Pricing.
- Extensive visualization of the backtest results.
- Analytical vs Empirical Backtest Match testing.
- Support for the Custom Pricing Backtest and Portfolio Backtest.
- Sensitivity Investigation over each instrument param.
- Robustness testing via Returns Shift.

## Project Structure

Here is the overview of the [/src/lib](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib) modules and the logic behind project design:

- [/src/lib/convolution.py](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib/convolution.py) <br />
Lets start with a simple task: from daily returns we'd like to get n-daily returns, where n is 
longevity of the option.<br />
One of the advantages of not using analytical functions for distributions is that we are able 
to just sum random variables (returns) instead of performing convolution. <br />
it's called 
Monte Carlo convolution.
- [/src/lib/kelly.py](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib/kelly.py) <br />
Now, Based on returns, strike and option type we can calculate premiums via reverse Kelly Criteria.<br />
Normally Kelly Criteria gives us optimal bet size based on the chance to win/loose and premia, 
which you get in the win case. <br />
In reverse case we know chances (based on given returns sample) and bet size (chosen by the user), 
so we are able to get optimal premium 
- [/src/lib/black_scholes.py](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib/black_scholes.py) <br />
Same story here: based on the returns sample we can calculate premiums via the BSM formula
- [/src/lib/random_path_generation.py](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib/random_path_generation.py) <br />
At this point we know what are the instruments and what premiums for those are going to be.<br />
It's reasonable to understand how relevant those premiums are. <br />
Since we've decided to use 
Monte Carlo backtest we need to generate multiple versions of the future: <br />
in this module we generate random paths to perform backtest on them later on
- [/src/lib/backtest.py](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib/backtest.py) <br />
Over here we can calculate pnl evolution for the Monte Carlo Paths and instrument provided. <br />
Also all the backtest results stats (sharpe, drawdown, etc.) live here.
- [/src/lib/plotting.py](https://github.com/potion-labs/interactive-WPs/tree/main/src/lib/plotting.py) <br />
Because we use Monte Carlo approach for the backtest we have many numbers (equal to number of random paths): <br />
e.g. Sharpe ratios, Max Drawdowns, etc. for each backtest. <br />
It leads us to having beautiful plots, which utilize the distributions 
of backtest results, showing risk/reward kde and many others.

## Roadmap

1. Make the project pip installable
2. Add extensive testing
3. Add analytical caclulations support

## Contributing

PRs/Issues are warmly welcome! <br />
Please mind styling and docs.

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

[Discord Community]

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[potion-shield]: https://img.shields.io/badge/Website-PotionLabs-purple
[potion-url]: https://potion.fi/
[twitter-potion-shield]: https://img.shields.io/twitter/follow/PotionLabs?label=Follow
[twitter-potion-url]: https://twitter.com/PotionLabs
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/company/potion-insurance
[medium-shield]: https://img.shields.io/badge/Medium-PotionLabs-brightgreen
[medium-url]: https://medium.com/@PotionLabs
[versions-shield]: https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue
[versions-url]: https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue
[potion-github-utl]: https://github.com/potion-labs
[license-shield]: https://img.shields.io/github/license/potion-labs/interactive-WPs.svg
[license-url]: https://github.com/potion-labs/interactive-WPs/blob/main/LICENSE

[discord-shield]: https://img.shields.io/discord/706193366056042496?style=social
[Discord Community]: https://discord.gg/YTtG4cxg

[potion-logo]: media/potion_logo.jpg

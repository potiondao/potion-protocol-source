from setuptools import setup, find_packages

f = open('requirements.txt')
required = f.read().splitlines()

setup(name='potion-analytics-thicc',
      version='1.0.0',
      description='Potion Analytics Tools for Thick Tailed probability. Contains curve generation '
                  'and backtesting tools for any continuous prob distribution, '
                  'including fat tailed ones. Includes ability to generate '
                  'kelly curves free of arbitrage.',
      packages=find_packages(),
      install_requires=required)

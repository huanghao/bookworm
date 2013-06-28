from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name="bookworm",
    version="0.1",
    scripts=['scripts/fixnames.py',
             'scripts/run_image_search.sh',
             'scripts/run_index.sh'],
    packages=find_packages(),
    )

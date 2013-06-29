from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
import glob

setup(
    name="bookworm",
    version="0.1",
    scripts=glob.glob('scripts/*.py') +
        glob.glob('scripts/*.sh'),
    packages=find_packages(),
    )

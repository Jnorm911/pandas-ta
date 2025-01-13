# -*- coding: utf-8 -*-
# setup.py
import re
from pathlib import Path
from setuptools import setup, find_packages

def read_version():
    ver_path = Path(__file__).parent / "pandas_ta_tnt" / "_version.py"
    content = ver_path.read_text()
    match = re.search(r'^__version__ = ["\']([^"\']*)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find __version__ in _version.py")

long_description = (
    "Pandas Technical Analysis, Pandas TA, is a free, ..."
)

setup(
    name="pandas_ta_tnt",
    version=read_version(),
    packages=find_packages(),
    description=long_description,
    long_description=long_description,
    author="Kevin Johnson",
    author_email="appliedmathkj@gmail.com",
    url="https://github.com/twopirllc/pandas-ta",
    maintainer="Kevin Johnson",
    maintainer_email="appliedmathkj@gmail.com",
    download_url="https://github.com/twopirllc/pandas-ta.git",
    keywords=[
        "technical analysis", "finance", "trading", "backtest", "trading bot",
        "features", "pandas", "numpy", "numba", "vectorbt", "yfinance",
        "polygon", "python3"
    ],
    license="The MIT License (MIT)",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    package_data={
        "pandas_ta_tnt": ["py.typed"],
        "data": ["data/*.csv"],
    },
    install_requires=[
        "numba>=0.60.0",
        "numpy>=2.0.0",
        "pandas>=2.2.3",
        "pandas-datareader>=0.10.0",
        "scipy>=1.15.1",
    ],
    extras_require={
        "full": [
            "alphaVantage-api",
            "matplotlib>=3.10.0",
            "mplfinance",
            "python-dotenv",
            "sklearn",
            "statsmodels",
            "stochastic",
            "TA-Lib>=0.6.0",
            "tqdm",
            "vectorbt",
            "yfinance>=0.2.51"
        ],
        "test": [
            "numba>=0.60.0",
            "numpy>=2.0.0",
            "pandas>=2.2.3",
            "pandas-datareader>=0.10.0",
            "pytest==7.1.2",
            "TA-Lib>=0.6.0",
            "yfinance>=0.2.51"
        ],
    },
)
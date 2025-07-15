'''Setup.py'''
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="dans",
    version="1.1.2",
    author="Oscar Gutierrez Altamirano",
    author_email="oscargutierreza617@gmail.com",
    description="A package for scraping data from basketball-reference.com and stats.nba.com" + \
        "to provide opponent-adjusted statistics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),

    install_requires=[
        "pandas>=2.2.3","numpy>=2.2.3","requests>=2.32.3","six>=1.16.0","Unidecode>=1.3.8","ratelimit>=2.2.1","bs4>=0.0.2","tqdm>=4.66.2","pylint>=3.3.5","build>=1.2.2.post1","lxml>=5.3.1","nba_api>=1.10.0","pytest>=7.4.0"
    ],

    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    keywords=[
        "nba",
        "nba.com",
        "stats.nba.com",
        "sports",
        "basketball",
        ],

    package_data = {'dans': ['dans/utils/*.txt']}
)

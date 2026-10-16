# PT World Download Fixer

Simple script to fix to fix polytoria worlds downloaded from the version history

Works and tested on linux, don't know how if it works on other operating systems :>

Requirements to install:
- [git](https://git-scm.com/install/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)


How to install and use it:
```shell
git clone https://github.com/c4pullin/PT-WorldDownloadFix/ PT-WorldDownloadFix/ 
cd PT-WorldDownloadFix/ 
uv sync
uv run PTWorldDownloadFix.py <input .poly file> <exported folder location>
```

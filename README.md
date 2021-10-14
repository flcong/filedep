# filedep: A small python tool to check file dependency

## Motivation

When doing empirical analysis, you may encounter the following issue about file
dependency. 

* Suppose `code.py` (or `code.do`, `code.sas`, `code.m`, `code.R`, etc)
  reads data from `indata.csv`, does some data cleaning, and then saves the 
  intermediary data as `outdata.csv`. 
  
* After using `outdata.csv` to run some statistical tests, you want to change 
  the data cleaning procedure a bit, so you modify `code.py`. 
  
* If there are only one code file and two data files, you will easily remember to
re-run `code.py` to update the output data `outdata.csv`. 
  
* However, suppose that `outdata.csv` is then used by `code2.py` to write 
  `finaldata.csv`. Then, people may easily forget to re-run `code2.py` as well
  to update `finaldata.csv`.
  
* As a result, this may cause the illusion that results change after you run
  the same set of code twice. For example, you forget to update `finaldata.csv`
  initially, but then accidentally update `finaldata.csv` some time later. Then,
  you find that results change after you run the same set of code.

To resolve this issue, I build this simple package to check file dependencies
based on last modified time. Users can define file dependencies, such as `code.py`
using `pre1.csv` and `pre2.csv` as input to write `post1.csv` and `post2.csv`.
Then, the function in the package will check if the last modified times of both
`pre1.csv` and `pre2.csv` are before that of `code.py` and the last modified 
times of both `post1.csv` and `post2.csv` are after that of `code.py`. If any
file dependency is broken, the broken ones will be printed or saved to a file.

## Installation

Use `pip` to install the package as follows:
```python 
pip install filedep
```

## Usage

Import the package using
```python
import filedep
```

The key function is `check_dep(deps, outfile=sys.stdout, reterr=False)`. 
The first argument is a list of dependencies (defined below). The second 
argument specifies where to print error information if any file dependency is 
broken. The default is `sys.stdout`. The third argument specifies if broken 
dependencies are returned from the function. This is mainly for testing 
purposes. The default is `False`, i.e., broken dependencies are only printed. 

The file dependencies have to be provided by the user using the format defined
below. In the `template` folder, there is a template to define dependencies
and use `check_dep()` function to check.

### Example 1. No broken file dependencies

The following code creates several empty files:
```python
import filedep
import time
import os
from os.path import join as pj

PATH = r'C:\test_check_dep'
if not os.path.exists(PATH):
    os.mkdir(PATH)

def touch(filepath):
    if os.path.exists(filepath):
        os.utime(filepath)
    else:
        with open(filepath, 'a') as f:
            pass

# Touch files in a specific order
touch(pj(PATH, 'pre11.csv'))
time.sleep(.1)
touch(pj(PATH, 'pre12.csv'))
time.sleep(.1)
touch(pj(PATH, 'code1.py'))
time.sleep(.1)
touch(pj(PATH, 'post11.csv'))
time.sleep(.1)
touch(pj(PATH, 'post12.csv'))
time.sleep(.1)

# Define dependencies
deps = [
    (
        [
            pj(PATH, 'pre11.csv'),
            pj(PATH, 'pre12.csv')
        ], 
        pj(PATH, 'code1.py'), 
        [
            pj(PATH, 'post11.csv'),
            pj(PATH, 'post12.csv'),
        ],
    ),
]
filedep.check_dep(deps)
```
In `deps`, we define a single dependency as follows: under the directory 
`C:\test_check_dep`, `code1.py` reads `pre11.csv` and `pre12.csv` to produce
`post11.csv` and `post12.csv`. Then, the last modified times of both `pre11.csv`
and `pre12.csv` must be before that of `code1.py` and those of both `post11.csv`
and `post12.csv` must be after that of `code1.py`

Since the dependency is satisfied by construction, the output is
```
All file dependencies are verified!
```

### Example 2. Broken file dependencies

The following code creates several empty files and define two broken dependencies:
```python
import filedep
import time
import os
from os.path import join as pj

PATH = r'C:\test_check_dep'
if not os.path.exists(PATH):
    os.mkdir(PATH)

def touch(filepath):
    if os.path.exists(filepath):
        os.utime(filepath)
    else:
        with open(filepath, 'a') as f:
            pass

# Touch files in a specific order
touch(pj(PATH, 'pre11.csv'))
time.sleep(.1)
touch(pj(PATH, 'pre12.csv'))
time.sleep(.1)
touch(pj(PATH, 'code1.py'))
time.sleep(.1)
touch(pj(PATH, 'post11.csv'))
time.sleep(.1)
# Note code1.py is newer than post11.csv
touch(pj(PATH, 'code1.py'))
time.sleep(.1)
touch(pj(PATH, 'post12.csv'))
time.sleep(.1)

# Define dependencies
deps = [
    (
        [
            pj(PATH, 'pre11.csv'),
        ], 
        pj(PATH, 'code1.py'), 
        [
            pj(PATH, 'post11.csv'),
        ],
    ),  
    (
        [
            pj(PATH, 'pre11.csv'),
            pj(PATH, 'pre12.csv'),
        ], 
        pj(PATH, 'code1.py'), 
        [
            pj(PATH, 'post11.csv'), 
            pj(PATH, 'post12.csv'),
        ],
    )
]
filedep.check_dep(deps)
```
Here, we define 2 dependencies. The second one is the same as that in the 
previous example, but the first one defines a simpler dependency: `code1.py` 
uses `pre11.csv` to produce `post11.csv`. Since by construction `post11.csv` is
"touched" before `code1.py`, both dependencies are broken. Hence, the output is
```
There are 2 broken file dependencies!!! 
[1]
                                           Last Modified Time
  Input:
    C:\test_check_dep\pre11.csv      : 2021-10-14 14:25:11.011976
  Code:
    C:\test_check_dep\code1.py       : 2021-10-14 14:25:11.451668
  Output:
    C:\test_check_dep\post11.csv     : 2021-10-14 14:25:11.342247
[2]
                                           Last Modified Time
  Input:
    C:\test_check_dep\pre11.csv      : 2021-10-14 14:25:11.011976
    C:\test_check_dep\pre12.csv      : 2021-10-14 14:25:11.125543
  Code:
    C:\test_check_dep\code1.py       : 2021-10-14 14:25:11.451668
  Output:
    C:\test_check_dep\post11.csv     : 2021-10-14 14:25:11.342247
    C:\test_check_dep\post12.csv     : 2021-10-14 14:25:11.559796
```
where the last modified date of each file in each broken dependency is shown.


## Format of file dependency

The first argument of `check_dep()` is a list of dependencies. Its format 
should be as follows:

* It is a list of tuples.
* Each tuple has three elements.
    - The first element is a list of `str`.
    - The second element is a `str`.
    - The third element is a list of `str`.
    - Each `str` is an absolute path of a existing file.
  
As an example, the following code defines two dependencies:
```python
deps = [
    (
        ['pre1.txt'], 'code1.py', ['post1.txt']
    ),
    (
        ['pre21.txt', 'pre22.txt'], 'code2.py', ['post21.txt', 'post22.txt']
    )
]
```
* The first one says that `code1.py` uses `pre1.txt` as input and outputs 
`post1.txt`. As a result, the last modified date of the three files
should satisfy `pre1.txt<=code1.py<=post1.txt`.
* The second one says that `code2.py` uses `pre21.txt` and `pre22.txt` as input
  and outputs `post21.txt` and `post22.txt`. As a result, the last modified date
  of the three files should satisfy 
  `max(pre21.txt,pre22.txt)<=code1.py<=min(post21.txt,post22.txt)` where `max`
  (`min`) represent the maximum (minimum) date.



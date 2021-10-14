# This is a template to check file dependencies
import filedep
from os.path import join as pj

PATH = r'C:\test_check_dep'

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

# Check dependencies
filedep.check_dep(deps)
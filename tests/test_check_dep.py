import re
import time
import os
import pytest
from filedep import check_dep
import itertools


def test_format():
    # Check type of dependencies
    with pytest.raises(AssertionError, match='deps is not a list'):
        check_dep(5)
    # Check size of each dependency
    with pytest.raises(AssertionError,
                       match=re.escape('deps[0] does not have size 3')):
        check_dep([([], [])])
    # Check type of each dependency
    with pytest.raises(AssertionError,
                       match=re.escape('deps[0][0] is not a list')):
        check_dep([(1, "", [])])
        check_dep([([], "", 1)])
    with pytest.raises(AssertionError,
                       match=re.escape('deps[0][1] is not a str')):
        check_dep([([], 5, [])])
    # Existence of each file
    with pytest.raises(
            AssertionError,
            match=re.escape('The following file does not exist: preN.txt')):
        check_dep([(
            ['pre1.txt', 'preN.txt'], 'code1.txt', ['post1.txt', 'post21.txt']
        )])
    with pytest.raises(
            AssertionError,
            match=re.escape('The following file does not exist: codeN.txt')):
        check_dep([(
            ['pre1.txt', 'pre21.txt'], 'codeN.txt', ['post1.txt', 'post21.txt']
        )])
    with pytest.raises(
            AssertionError,
            match=re.escape('The following file does not exist: postN.txt')):
        check_dep([(
            ['pre1.txt', 'pre21.txt'], 'code1.txt', ['postN.txt', 'post1.txt']
        )])
        check_dep([(
            ['pre1.txt', 'pre21.txt'], '', ['postN.txt', 'post1.txt']
        )])


def test_time():
    deps = [
        (
            ['pre1.txt'], 'code1.txt', ['post1.txt']
        ),
        (
            ['pre21.txt', 'pre22.txt'], 'code2.txt', ['post21.txt', 'post22.txt']
        )
    ]
    # ---------- Single data file
    files = ['pre1.txt', 'code1.txt', 'post1.txt']
    perms = list(itertools.permutations(range(3)))
    for perm in perms:
        if not perm[0] < perm[1] < perm[2]:
            for i in range(3):
                os.utime(files[perm[i]])
                time.sleep(.01)
            errdep = check_dep(deps[:1], reterr=True)
            assert errdep is not None
            assert len(errdep) == 1
            assert list(errdep[0][0].keys())[0] == 'pre1.txt'
            assert list(errdep[0][1].keys())[0] == 'code1.txt'
            assert list(errdep[0][2].keys())[0] == 'post1.txt'

    # ---------- Multiple data file
    # Break dependency 1
    os.utime('code1.txt')
    time.sleep(.01)
    os.utime('pre1.txt')
    time.sleep(.01)
    os.utime('post1.txt')
    files = ['pre21.txt', 'pre22.txt', 'code2.txt', 'post21.txt', 'post22.txt']
    perms = list(itertools.permutations(range(5)))
    for perm in perms:
        if not (
            perm[2] == 2 and
            ((perm[0] == 0 and perm[1] == 1) or
             (perm[0] == 1 and perm[1] == 0)) and
            ((perm[3] == 3 and perm[4] == 4) or
             (perm[3] == 4 and perm[4] == 3))
        ):
            for i in range(5):
                os.utime(files[perm[i]])
                time.sleep(.01)
            errdep = check_dep(deps, reterr=True)
            assert errdep is not None
            assert len(errdep) == 2
            # 1st
            assert list(errdep[0][0].keys())[0] == 'pre1.txt'
            assert list(errdep[0][1].keys())[0] == 'code1.txt'
            assert list(errdep[0][2].keys())[0] == 'post1.txt'
            # 2nd
            assert list(errdep[1][0].keys())[0] == 'pre21.txt'
            assert list(errdep[1][0].keys())[1] == 'pre22.txt'
            assert list(errdep[1][1].keys())[0] == 'code2.txt'
            assert list(errdep[1][2].keys())[0] == 'post21.txt'
            assert list(errdep[1][2].keys())[1] == 'post22.txt'

# DEPRECATED

this library is no longer needed:

- python 2 and python3.5 have reached end of life
- micropython added f-strings support

___

[![Build Status](https://asottile.visualstudio.com/asottile/_apis/build/status/asottile.future-fstrings?branchName=master)](https://asottile.visualstudio.com/asottile/_build/latest?definitionId=15&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/asottile/asottile/15/master.svg)](https://dev.azure.com/asottile/asottile/_build/latest?definitionId=15&branchName=master)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/asottile/future-fstrings/master.svg)](https://results.pre-commit.ci/latest/github/asottile/future-fstrings/master)

future-fstrings
===============

A backport of fstrings to python<3.6.


## Installation

`pip install future-fstrings`


## Usage

Include the following encoding cookie at the top of your file (this replaces
the utf-8 cookie if you already have it):

```python
# -*- coding: future_fstrings -*-
```

And then write python3.6 fstring code as usual!

```python
# -*- coding: future_fstrings -*-
thing = 'world'
print(f'hello {thing}')
```

```console
$ python2.7 main.py
hello world
```

## Showing transformed source

`future-fstrings` also includes a cli to show transformed source.

```console
$ future-fstrings-show main.py
# -*- coding: future_fstrings -*-
thing = 'world'
print('hello {}'.format((thing)))
```

## Transform source for micropython

The `future-fstrings-show` command can be used to transform source before
distributing.  This can allow you to write f-string code but target platforms
which do not support f-strings, such as [micropython].

To use this on modern versions of python, install using:

```bash
pip install future-fstrings[rewrite]
```

and then use `future-fstrings-show` as above.

For instance:

```bash
future-fstrings-show code.py > code_rewritten.py
```

[micropython]: https://github.com/micropython/micropython

## How does this work?

`future-fstrings` has two parts:

1. A utf-8 compatible `codec` which performs source manipulation
    - The `codec` first decodes the source bytes using the UTF-8 codec
    - The `codec` then leverages
      [tokenize-rt](https://github.com/asottile/tokenize-rt) to rewrite
      f-strings.
2. A `.pth` file which registers a codec on interpreter startup.

## when you aren't using normal `site` registration

in setups (such as aws lambda) where you utilize `PYTHONPATH` or `sys.path`
instead of truly installed packages, the `.pth` magic above will not take.

for those circumstances, you'll need to manually initialize `future-fstrings`
in a non-fstring wrapper.  for instance:

```python
import future_fstrings

future_fstrings.register()

from actual_main import main

if __name__ == '__main__':
    raise SystemExit(main())
```

## you may also like

- [future-annotations](https://github.com/asottile/future-annotations)
- [future-breakpoint](https://github.com/asottile/future-breakpoint)

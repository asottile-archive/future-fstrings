[![Build Status](https://travis-ci.org/asottile/future-fstrings.svg?branch=master)](https://travis-ci.org/asottile/future-fstrings)
[![Coverage Status](https://coveralls.io/repos/github/asottile/future-fstrings/badge.svg?branch=reimplement_string_parser)](https://coveralls.io/github/asottile/future-fstrings?branch=reimplement_string_parser)

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

## How does this work?

`future-fstrings` has two parts:

1. A utf-8 compatible `codec` which performs source manipulation
    - The `codec` first decodes the source bytes using the UTF-8 codec
    - The `codec` then leverages
      [tokenize-rt](https://github.com/asottile/tokenize-rt) to rewrite
      f-strings.
2. A `.pth` file which registers a codec on interpreter startup.

[![Build Status](https://travis-ci.org/asottile/future-fstrings.svg?branch=master)](https://travis-ci.org/asottile/future-fstrings)

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


## How does this work?

`future-fstrings` has two parts:

1. A utf-8 compatible `codec` which performs source manipulation
    - The `codec` first decodes the source bytes using the UTF-8 codec
    - The `codec` then leverages
      [tokenize-rt](https://github.com/asottile/tokenize-rt) to rewrite
      f-strings.
2. A `.pth` file which registers a codec on interpreter startup.

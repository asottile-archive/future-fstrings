from __future__ import absolute_import
from __future__ import unicode_literals

import codecs

encode = codecs.utf_8_encode


def _find_literal(s, start, level, parts, exprs):
    """Roughly Python.ast.c:fstring_find_literal"""
    i = start
    parse_expr = True

    while i < len(s):
        ch = s[i]

        if ch in ('{', '}'):
            if level == 0:
                if i + 1 < len(s) and s[i + 1] == ch:
                    i += 2
                    parse_expr = False
                    break
                elif ch == '}':
                    raise AssertionError("f-string: single '}' is not allowed")
            break

        i += 1

    parts.append(s[start:i])
    return i, parse_expr and i < len(s)


def _find_expr(s, start, level, parts, exprs):
    """Roughly Python.ast.c:fstring_find_expr"""
    i = start
    nested_depth = 0
    quote_char = None
    triple_quoted = None

    def _check_end():
        if i == len(s):
            raise AssertionError("f-string: expecting '}'")

    if level >= 2:
        raise AssertionError("f-string: expressions nested too deeply")

    parts.append(s[i])
    i += 1

    while i < len(s):
        ch = s[i]

        if ch == '\\':
            raise AssertionError(
                'f-string expression part cannot include a backslash',
            )
        if quote_char is not None:
            if ch == quote_char:
                if triple_quoted:
                    if i + 2 < len(s) and s[i + 1] == ch and s[i + 2] == ch:
                        i += 2
                        quote_char = None
                        triple_quoted = None
                else:
                    quote_char = None
                    triple_quoted = None
        elif ch in ('"', '"'):
            quote_char = ch
            if i + 2 < len(s) and s[i + 1] == ch and s[i + 2] == ch:
                triple_quoted = True
                i += 2
            else:
                triple_quoted = False
        elif ch in ('[', '{', '('):
            nested_depth += 1
        elif nested_depth and ch in (']', '}', ')'):
            nested_depth -= 1
        elif ch == '#':
            raise AssertionError("f-string expression cannot include '#'")
        elif nested_depth == 0 and ch in ('!', ':', '}'):
            if ch == '!' and i + 1 < len(s) and s[i + 1] == '=':
                # Allow != at top level as `=` isn't a valid conversion
                pass
            else:
                break
        i += 1

    if quote_char is not None:
        raise AssertionError('f-string: unterminated string')
    elif nested_depth:
        raise AssertionError("f-string: mismatched '(', '{', or '['")
    _check_end()

    exprs.append(s[start + 1:i])

    if s[i] == '!':
        parts.append(s[i])
        i += 1
        _check_end()
        parts.append(s[i])
        i += 1

    _check_end()

    if s[i] == ':':
        parts.append(s[i])
        i += 1
        _check_end()
        i = _fstring_parse(s, i, level + 1, parts, exprs)

    _check_end()
    if s[i] != '}':
        raise AssertionError("f-string: expecting '}'")

    parts.append(s[i])
    i += 1
    return i


def _fstring_parse(s, i, level, parts, exprs):
    """Roughly Python.ast.c:fstring_find_literal_and_expr"""
    while True:
        i, parse_expr = _find_literal(s, i, level, parts, exprs)
        if i == len(s) or s[i] == '}':
            return i
        if parse_expr:
            i = _find_expr(s, i, level, parts, exprs)


def _fstring_reformat(s):
    parts, exprs = [], []
    _fstring_parse(s, i=0, level=0, parts=parts, exprs=exprs)
    exprs = ['({})'.format(expr) for expr in exprs]
    return '{}.format({})'.format(''.join(parts), ', '.join(exprs))


def _make_fstring(src):
    import tokenize_rt

    return [tokenize_rt.Token(name='FSTRING', src=_fstring_reformat(src))]


def decode(b, errors='strict'):
    import tokenize_rt

    u, l = codecs.utf_8_decode(b, errors)
    tokens = tokenize_rt.src_to_tokens(u)
    for i, token in reversed(tuple(enumerate(tokens))):
        if (
                token.name == 'NAME' and
                token.src == 'f' and
                tokens[i + 1].name == 'STRING'
        ):
            tokens[i:i + 2] = _make_fstring(tokens[i + 1].src)
    return tokenize_rt.tokens_to_src(tokens), l


def _natively_supports_fstrings():
    try:
        return eval('f"hi"') == 'hi'
    except SyntaxError:
        return False


SUPPORTS_FSTRINGS = _natively_supports_fstrings()
if SUPPORTS_FSTRINGS:  # pragma: no cover
    decode = codecs.utf_8_decode  # noqa


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, s, final=False):  # pragma: no cover
        return encode(s, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def decode(self, b, final=False):  # pragma: no cover
        return decode(b, self.errors)[0]


class Codec(codecs.Codec):
    def encode(self, s, errors='strict'):  # pragma: no cover
        return encode(s, errors)

    def decode(self, b, errors='strict'):  # pragma: no cover
        return decode(b, errors)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


# codec api

codec_map = {
    name: codecs.CodecInfo(
        name=name,
        encode=encode,
        decode=decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )
    for name in ('future-fstrings', 'future_fstrings')
}


def register():  # pragma: no cover
    codecs.register(codec_map.get)

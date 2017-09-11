import codecs
import re
import string

encode = codecs.utf_8_encode

_parse_format = string.Formatter().parse

_start_quote_re = re.compile('^[a-z]*(\'|"|\'\'\'|""")')
_end_quote_re = re.compile('(\'|"|\'\'\'|""")$')


def _make_fstring(src):
    import tokenize_rt

    parts = []

    def _convert_tup(tup):
        ret, field_name, format_spec, conversion = tup
        ret = ret.replace('{', '{{').replace('}', '}}')
        if field_name is not None:
            parts.append(field_name)
            ret += '{'
            if conversion:
                ret += '!' + conversion
            if format_spec:
                ret += ':' + format_spec
            ret += '}'
        return ret

    new_str = ''.join(_convert_tup(tup) for tup in _parse_format(src))
    new_src = '{}.format({})'.format(new_str, ', '.join(parts))
    return [tokenize_rt.Token(name='FSTRING', src=new_src)]


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
if SUPPORTS_FSTRINGS:
    decode = codecs.utf_8_decode  # noqa


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, s, final=False):
        return encode(s, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def decode(self, b, final=False):
        return decode(b, self.errors)[0]


class Codec(codecs.Codec):
    def encode(self, s, errors='strict'):
        return encode(s, errors)

    def decode(self, b, errors='strict'):
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


def register():
    codecs.register(codec_map.get)

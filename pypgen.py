import re

class Success:
    """ Indicates parse success """

    def __init__(self, value, rest):
        self.value = value
        self.rest = rest

    def __str__(self):
        return "Success(%s, %s)" % (self.value, self.rest)


class Failure:
    """ Indicates parse failure """

    def __init__(self, expected, rest):
        self.expected = expected
        self.rest = rest

    def __str__(self):
        return "Failure(%s, %s)" % (self.expected, self.rest)


class Parser:
    """ Base class for parsers, supplies some useful methods """

    def then(self, next_parser):
        return SeqParser(self, next_parser)

    def oor(self, alt_parser):
        return OrParser(self, alt_parser)

    def w(self, trans):
        return ResultTransformingParser(self, trans)


class ResultTransformingParser(Parser):
    """ Wrapper to apply transformations to parse results """

    def __init__(self, parser, trans):
        self.parser = parser
        self.trans = trans

    def parse(self, in_str):
        result = self.parser.parse(in_str)
        if isinstance(result, Failure):
            return result

        return Success(self.trans(result.value), result.rest)

    def __str__(self):
        return "ResultTransformingParser(%s, %s)" % (self.parser, self.trans)


class SeqParser(Parser):
    """ Parse things that happen in sequence, in sequence """

    def __init__(self, *parsers):
        self.parsers = parsers

    def parse(self, in_str):
        result_values = []
        in_str_rest = in_str
        for parser in self.parsers:
            result = parser.parse(in_str_rest)
            if isinstance(result, Failure):
                return result
            else:
                result_values.append(result.value)
                in_str_rest = result.rest
        
        return Success(tuple(result_values), in_str_rest)

    def then(self, *parsers):
        return SeqParser(*(self.parsers + parsers))

    def __str__(self):
        return "SeqParser(%s)" % ([str(p) for p in self.parsers])


class OrParser(Parser):
    """ Parse things with alternates """

    def __init__(self, *parsers):
        self.parsers = parsers

    def parse(self, in_str):
        for parser in self.parsers:
            result = parser.parse(in_str)
            if isinstance(result, Success):
                return result

        return Failure([str(p) for p in self.parsers], in_str)

    def oor(self, *parsers):
        return OrParser(*(self.parsers + parsers))


class KleeneParser(Parser):
    """ Parse something that happens 0 or more times """

    def __init__(self, parser):
        self.parser = parser

    def parse(self, in_str):
        results = []
        result = self.parser.parse(in_str)
        while isinstance(result, Success):
            results.append(result.value)
            result = self.parser.parse(result.rest)
        return Success(results, result.rest)

    def __str__(self):
        return "KleeneParser(%s)" % self.parser


class RegexParser(Parser):
    """ Parse based on a regex """

    def __init__(self, regex_str):
        self.regex = re.compile(regex_str)

    def parse(self, in_str):
        match = self.regex.match(in_str)
        if match is not None:
            return Success(match.group(), in_str[match.end():])
        else:
            return Failure(self.regex.pattern, in_str)

    def __str__(self):
        return "RegexParser(%s)" % (self.regex.pattern)


class LiteralParser(Parser):
    """ Parse based on a literal """

    def __init__(self, s):
        self.s = s

    def parse(self, in_str):
        if in_str.startswith(self.s):
            # do this for copy... forget how python does this
            return Success(in_str[:len(self.s)], in_str[len(self.s):])
        else:
            return Failure(self.s, in_str)

    def __str__(self):
        return "LiteralParser(%s)" % self.s


def parse(parser, in_str):
    """ Useful wrapper, just calls parse, but could do more """
    return parser.parse(in_str)

def r(regex_str):
    """ Convenience/sugar for creating RegexParser """
    return RegexParser(regex_str)

def rep(parser):
    """ Convenience/sugar for creating KleeneParser """
    return KleeneParser(parser)

def l(s):
    """ Convenience/sugar for creating literal parser """
    return LiteralParser(s)

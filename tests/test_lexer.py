from asl.lexer import Lexer
from asl.tokens import TokenType


def test_lexer_tokenizes_say_statement():
    tokens = Lexer('say "Hello";').tokenize()

    assert [token.type for token in tokens] == [
        TokenType.SAY,
        TokenType.STRING,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert tokens[1].lexeme == "Hello"


def test_lexer_ignores_comments():
    tokens = Lexer('# comment\nsay "Hello";').tokenize()

    assert tokens[0].type is TokenType.SAY


def test_lexer_tokenizes_add_statement():
    tokens = Lexer("add sugar = 100;").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.ADD,
        TokenType.IDENT,
        TokenType.ASSIGN,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert tokens[1].lexeme == "sugar"
    assert tokens[3].lexeme == "100"


def test_lexer_tokenizes_float_number():
    tokens = Lexer("add sugar = 2.5;").tokenize()

    assert tokens[3].type is TokenType.NUMBER
    assert tokens[3].lexeme == "2.5"


def test_lexer_tokenizes_operators_and_parens():
    tokens = Lexer("say (1 + 2) * 3 - 4 / 2;").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.SAY,
        TokenType.LPAREN,
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.RPAREN,
        TokenType.STAR,
        TokenType.NUMBER,
        TokenType.MINUS,
        TokenType.NUMBER,
        TokenType.SLASH,
        TokenType.NUMBER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_lexer_treats_unknown_word_as_identifier():
    tokens = Lexer("foo;").tokenize()

    assert tokens[0].type is TokenType.IDENT
    assert tokens[0].lexeme == "foo"


def test_lexer_tokenizes_if_statement():
    source = 'if sugar > 50 { say "甘い！"; } else { say "ちょうどいい"; }'
    tokens = Lexer(source).tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IF,
        TokenType.IDENT,
        TokenType.GT,
        TokenType.NUMBER,
        TokenType.LBRACE,
        TokenType.SAY,
        TokenType.STRING,
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.ELSE,
        TokenType.LBRACE,
        TokenType.SAY,
        TokenType.STRING,
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.EOF,
    ]


def test_lexer_tokenizes_comparison_operators():
    tokens = Lexer("say a == b; say a != b; say a <= b; say a >= b;").tokenize()

    types = [token.type for token in tokens]
    assert TokenType.EQ in types
    assert TokenType.NEQ in types
    assert TokenType.LTE in types
    assert TokenType.GTE in types


def test_lexer_tokenizes_bool_literals():
    tokens = Lexer("say true; say false;").tokenize()

    assert tokens[1].type is TokenType.TRUE
    assert tokens[4].type is TokenType.FALSE


def test_lexer_tokenizes_repeat_statement():
    tokens = Lexer('repeat 3 { say "かき混ぜる"; }').tokenize()

    assert [token.type for token in tokens] == [
        TokenType.REPEAT,
        TokenType.NUMBER,
        TokenType.LBRACE,
        TokenType.SAY,
        TokenType.STRING,
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.EOF,
    ]


def test_lexer_rejects_lone_exclamation():
    try:
        Lexer("say !true;").tokenize()
    except SyntaxError as error:
        assert "使えない文字 '!'" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_lexer_rejects_invalid_character():
    try:
        Lexer("say @;").tokenize()
    except SyntaxError as error:
        assert "使えない文字 '@'" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_lexer_rejects_unterminated_string():
    try:
        Lexer('say "Hello').tokenize()
    except SyntaxError as error:
        assert "unterminated string" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_lexer_reports_line_of_unterminated_string():
    try:
        Lexer('say "Hello\nWorld').tokenize()
    except SyntaxError as error:
        assert "line 2" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_lexer_rejects_non_ascii_digit():
    # '²' は str.isdigit() が真になるが int() で変換できない。
    # 数値リテラルとして拾うと Parser で ValueError になってしまうため、
    # 字句解析の段階で「使えない文字」として弾く。
    try:
        Lexer("say \u00b2;").tokenize()
    except SyntaxError as error:
        assert "使えない文字" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")

from asl.ast import (
    AddStatement,
    AssignStatement,
    BinaryExpr,
    BoolLiteral,
    Identifier,
    IfStatement,
    NumberLiteral,
    RepeatStatement,
    SayStatement,
    StringLiteral,
)
from asl.lexer import Lexer
from asl.parser import Parser


def _parse(source: str) -> list[object]:
    return Parser(Lexer(source).tokenize()).parse()


def test_parser_creates_say_statement():
    tokens = Lexer('say "Hello";').tokenize()
    statements = Parser(tokens).parse()

    assert len(statements) == 1
    assert isinstance(statements[0], SayStatement)
    assert statements[0].expression.value == "Hello"


def test_parser_rejects_missing_semicolon():
    tokens = Lexer('say "Hello"').tokenize()

    try:
        Parser(tokens).parse()
    except SyntaxError as error:
        assert "';' が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_creates_add_statement():
    statements = _parse("add sugar = 100;")

    assert statements == [AddStatement("sugar", NumberLiteral(100), 1)]


def test_parser_creates_assign_statement():
    statements = _parse("sugar = 200;")

    assert statements == [AssignStatement("sugar", NumberLiteral(200), 1)]


def test_parser_rejects_add_without_name():
    try:
        _parse("add = 100;")
    except SyntaxError as error:
        assert "add の後に変数名が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_assignment_without_equals():
    try:
        _parse('foo "Hello";')
    except SyntaxError as error:
        assert "'=' が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_unknown_statement_start():
    try:
        _parse("123;")
    except SyntaxError as error:
        assert "say / add / 代入 / if / repeat から始めてください" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_respects_arithmetic_precedence():
    statements = _parse("say 1 + 2 * 3;")

    assert statements == [
        SayStatement(
            BinaryExpr(
                NumberLiteral(1),
                "+",
                BinaryExpr(NumberLiteral(2), "*", NumberLiteral(3), 1),
                1,
            )
        )
    ]


def test_parser_respects_parentheses():
    statements = _parse("say (1 + 2) * 3;")

    assert statements == [
        SayStatement(
            BinaryExpr(
                BinaryExpr(NumberLiteral(1), "+", NumberLiteral(2), 1),
                "*",
                NumberLiteral(3),
                1,
            )
        )
    ]


def test_parser_parses_float_and_identifier():
    statements = _parse("add total = sugar + 2.5;")

    assert statements == [
        AddStatement(
            "total",
            BinaryExpr(Identifier("sugar", 1), "+", NumberLiteral(2.5), 1),
            1,
        )
    ]


def test_parser_parses_unary_minus():
    statements = _parse("say -3;")

    assert statements == [
        SayStatement(BinaryExpr(NumberLiteral(0), "-", NumberLiteral(3), 1))
    ]


def test_parser_rejects_missing_expression():
    try:
        _parse("say ;")
    except SyntaxError as error:
        assert "式が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_creates_if_statement():
    statements = _parse('if sugar > 50 { say "甘い！"; }')

    assert statements == [
        IfStatement(
            BinaryExpr(Identifier("sugar", 1), ">", NumberLiteral(50), 1),
            [SayStatement(StringLiteral("甘い！"))],
            None,
            1,
        )
    ]


def test_parser_creates_if_else_statement():
    statements = _parse(
        'if sugar > 50 { say "甘い！"; } else { say "ちょうどいい"; }'
    )

    assert statements == [
        IfStatement(
            BinaryExpr(Identifier("sugar", 1), ">", NumberLiteral(50), 1),
            [SayStatement(StringLiteral("甘い！"))],
            [SayStatement(StringLiteral("ちょうどいい"))],
            1,
        )
    ]


def test_parser_parses_nested_if():
    statements = _parse('if true { if false { say "a"; } else { say "b"; } }')

    assert statements == [
        IfStatement(
            BoolLiteral(True),
            [
                IfStatement(
                    BoolLiteral(False),
                    [SayStatement(StringLiteral("a"))],
                    [SayStatement(StringLiteral("b"))],
                    1,
                )
            ],
            None,
            1,
        )
    ]


def test_parser_comparison_is_looser_than_addition():
    statements = _parse("say 1 + 2 > 2;")

    assert statements == [
        SayStatement(
            BinaryExpr(
                BinaryExpr(NumberLiteral(1), "+", NumberLiteral(2), 1),
                ">",
                NumberLiteral(2),
                1,
            )
        )
    ]


def test_parser_rejects_missing_lbrace():
    try:
        _parse('if true say "a";')
    except SyntaxError as error:
        assert "'{' が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_missing_rbrace():
    try:
        _parse('if true { say "a";')
    except SyntaxError as error:
        assert "'}' が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_creates_repeat_statement():
    statements = _parse('repeat 3 { say "かき混ぜる"; }')

    assert statements == [
        RepeatStatement(
            NumberLiteral(3), [SayStatement(StringLiteral("かき混ぜる"))], 1
        )
    ]


def test_parser_creates_repeat_with_variable_count():
    statements = _parse("repeat times { say \"a\"; }")

    assert statements == [
        RepeatStatement(
            Identifier("times", 1), [SayStatement(StringLiteral("a"))], 1
        )
    ]


def test_parser_creates_nested_repeat():
    statements = _parse('repeat 2 { repeat 2 { say "a"; } }')

    assert statements == [
        RepeatStatement(
            NumberLiteral(2),
            [
                RepeatStatement(
                    NumberLiteral(2), [SayStatement(StringLiteral("a"))], 1
                )
            ],
            1,
        )
    ]


def test_parser_rejects_repeat_without_count():
    try:
        _parse('repeat { say "a"; }')
    except SyntaxError as error:
        assert "式が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_repeat_without_lbrace():
    try:
        _parse("repeat 3 say \"a\";")
    except SyntaxError as error:
        assert "'{' が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_else_without_if():
    try:
        _parse('else { say "a"; }')
    except SyntaxError as error:
        assert "say / add / 代入 / if / repeat から始めてください" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_missing_rparen():
    try:
        _parse("say (1 + 2;")
    except SyntaxError as error:
        assert "')' が必要です" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_too_long_integer_literal():
    source = "say " + "1" * 5000 + ";"
    try:
        _parse(source)
    except SyntaxError as error:
        assert "数値が大きすぎます" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")


def test_parser_rejects_float_literal_overflowing_to_inf():
    source = "say " + "9" * 400 + ".0;"
    try:
        _parse(source)
    except SyntaxError as error:
        assert "数値が大きすぎます" in str(error)
    else:
        raise AssertionError("SyntaxError was not raised")

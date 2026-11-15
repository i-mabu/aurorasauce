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
from asl.evaluator import Evaluator


def test_evaluator_prints_say_statement(capsys):
    statements = [SayStatement(StringLiteral("Hello"))]

    Evaluator().evaluate(statements)

    captured = capsys.readouterr()
    assert captured.out == "AURORA: Hello\n"


def test_evaluator_rejects_unknown_node():
    try:
        Evaluator().evaluate([object()])
    except RuntimeError as error:
        assert "unknown AST node" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_add_and_say_variable(capsys):
    statements = [
        AddStatement("sugar", NumberLiteral(100), 1),
        SayStatement(Identifier("sugar", 2)),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: 100\n"


def test_evaluator_assign_updates_variable(capsys):
    statements = [
        AddStatement("sugar", NumberLiteral(100), 1),
        AssignStatement("sugar", NumberLiteral(150), 2),
        SayStatement(Identifier("sugar", 3)),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: 150\n"


def test_evaluator_calculates_arithmetic(capsys):
    statements = [
        SayStatement(
            BinaryExpr(
                BinaryExpr(NumberLiteral(1), "+", NumberLiteral(2), 1),
                "*",
                NumberLiteral(3),
                1,
            )
        ),
        SayStatement(BinaryExpr(NumberLiteral(10), "/", NumberLiteral(4), 2)),
        SayStatement(BinaryExpr(NumberLiteral(7), "-", NumberLiteral(2), 3)),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: 9\nAURORA: 2.5\nAURORA: 5\n"


def test_evaluator_concatenates_strings(capsys):
    statements = [
        AddStatement("total", NumberLiteral(200), 1),
        SayStatement(
            BinaryExpr(
                BinaryExpr(
                    StringLiteral("合計: "), "+", Identifier("total", 2), 2
                ),
                "+",
                StringLiteral("g"),
                2,
            )
        ),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: 合計: 200g\n"


def test_evaluator_rejects_undefined_variable():
    try:
        Evaluator().evaluate([SayStatement(Identifier("sugar", 3))])
    except RuntimeError as error:
        assert "line 3" in str(error)
        assert "変数 'sugar' は定義されていません" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_assign_to_undefined_variable():
    try:
        Evaluator().evaluate([AssignStatement("sugar", NumberLiteral(1), 2)])
    except RuntimeError as error:
        assert "変数 'sugar' は定義されていません" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_redefine_with_add():
    statements = [
        AddStatement("sugar", NumberLiteral(100), 1),
        AddStatement("sugar", NumberLiteral(200), 2),
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "変数 'sugar' はすでに定義されています" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_division_by_zero():
    statements = [
        SayStatement(BinaryExpr(NumberLiteral(1), "/", NumberLiteral(0), 1))
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "0 で割ることはできません" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_unknown_expression():
    try:
        Evaluator().evaluate([SayStatement(object())])
    except RuntimeError as error:
        assert "unknown AST node" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_unknown_operator():
    statements = [
        SayStatement(BinaryExpr(NumberLiteral(1), "%", NumberLiteral(2), 1))
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "知らない演算子 '%'" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_runs_if_branch(capsys):
    statements = [
        IfStatement(
            BoolLiteral(True),
            [SayStatement(StringLiteral("はい"))],
            [SayStatement(StringLiteral("いいえ"))],
            1,
        )
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: はい\n"


def test_evaluator_runs_else_branch(capsys):
    statements = [
        IfStatement(
            BoolLiteral(False),
            [SayStatement(StringLiteral("はい"))],
            [SayStatement(StringLiteral("いいえ"))],
            1,
        )
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: いいえ\n"


def test_evaluator_runs_nothing_without_else(capsys):
    statements = [
        IfStatement(BoolLiteral(False), [SayStatement(StringLiteral("はい"))], None, 1)
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == ""


def test_evaluator_rejects_non_bool_condition():
    statements = [
        IfStatement(NumberLiteral(1), [SayStatement(StringLiteral("はい"))], None, 2)
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "line 2" in str(error)
        assert "if の条件は true か false で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_compares_numbers(capsys):
    statements = [
        SayStatement(BinaryExpr(NumberLiteral(3), "<", NumberLiteral(5), 1)),
        SayStatement(BinaryExpr(NumberLiteral(5), "<=", NumberLiteral(5), 2)),
        SayStatement(BinaryExpr(NumberLiteral(5), ">", NumberLiteral(3), 3)),
        SayStatement(BinaryExpr(NumberLiteral(3), ">=", NumberLiteral(5), 4)),
        SayStatement(BinaryExpr(NumberLiteral(5), "==", NumberLiteral(5), 5)),
        SayStatement(BinaryExpr(NumberLiteral(5), "!=", NumberLiteral(5), 6)),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == (
        "AURORA: true\n"
        "AURORA: true\n"
        "AURORA: true\n"
        "AURORA: false\n"
        "AURORA: true\n"
        "AURORA: false\n"
    )


def test_evaluator_compares_strings(capsys):
    statements = [
        SayStatement(
            BinaryExpr(StringLiteral("a"), "==", StringLiteral("a"), 1)
        ),
        SayStatement(
            BinaryExpr(StringLiteral("a"), "!=", StringLiteral("b"), 2)
        ),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: true\nAURORA: true\n"


def test_evaluator_rejects_ordering_bool():
    statements = [
        SayStatement(
            BinaryExpr(BoolLiteral(True), "<", NumberLiteral(2), 1)
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "比べられるのは数値だけです" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_ordering_strings():
    statements = [
        SayStatement(
            BinaryExpr(StringLiteral("a"), "<", StringLiteral("b"), 1)
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "比べられるのは数値だけです" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_prints_bool_as_true_false(capsys):
    statements = [
        SayStatement(BoolLiteral(True)),
        SayStatement(BoolLiteral(False)),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: true\nAURORA: false\n"


def test_evaluator_repeats_body(capsys):
    statements = [
        RepeatStatement(
            NumberLiteral(3), [SayStatement(StringLiteral("かき混ぜる"))], 1
        )
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == (
        "AURORA: かき混ぜる\n" "AURORA: かき混ぜる\n" "AURORA: かき混ぜる\n"
    )


def test_evaluator_repeats_zero_times(capsys):
    statements = [
        RepeatStatement(
            NumberLiteral(0), [SayStatement(StringLiteral("出ない"))], 1
        )
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == ""


def test_evaluator_repeats_variable_count(capsys):
    statements = [
        AddStatement("times", NumberLiteral(2), 1),
        RepeatStatement(
            Identifier("times", 2), [SayStatement(StringLiteral("もう一度"))], 2
        ),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: もう一度\nAURORA: もう一度\n"


def test_evaluator_repeats_expression_count(capsys):
    statements = [
        RepeatStatement(
            BinaryExpr(NumberLiteral(1), "+", NumberLiteral(1), 1),
            [SayStatement(StringLiteral("a"))],
            1,
        )
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == "AURORA: a\nAURORA: a\n"


def test_evaluator_rejects_negative_repeat():
    statements = [
        RepeatStatement(
            NumberLiteral(-1), [SayStatement(StringLiteral("a"))], 1
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "repeat の回数は 0 以上で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_fractional_repeat():
    statements = [
        RepeatStatement(
            NumberLiteral(2.5), [SayStatement(StringLiteral("a"))], 1
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "repeat の回数は整数で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_string_repeat():
    statements = [
        RepeatStatement(
            StringLiteral("3"), [SayStatement(StringLiteral("a"))], 1
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "repeat の回数は数値で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_bool_repeat():
    statements = [
        RepeatStatement(
            BoolLiteral(True), [SayStatement(StringLiteral("a"))], 1
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "repeat の回数は数値で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_calculating_with_bool():
    statements = [
        SayStatement(BinaryExpr(BoolLiteral(True), "+", NumberLiteral(1), 1))
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "計算できるのは数値だけです" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_calculating_with_string():
    statements = [
        SayStatement(
            BinaryExpr(StringLiteral("a"), "-", StringLiteral("b"), 1)
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "計算できるのは数値だけです" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_distinguishes_bool_from_number_in_equality(capsys):
    statements = [
        SayStatement(BinaryExpr(NumberLiteral(1), "==", BoolLiteral(True), 1)),
        SayStatement(BinaryExpr(NumberLiteral(0), "==", BoolLiteral(False), 1)),
        SayStatement(BinaryExpr(NumberLiteral(1), "!=", BoolLiteral(True), 1)),
        SayStatement(BinaryExpr(BoolLiteral(True), "==", BoolLiteral(True), 1)),
    ]

    Evaluator().evaluate(statements)

    assert capsys.readouterr().out == (
        "AURORA: false\n" "AURORA: false\n" "AURORA: true\n" "AURORA: true\n"
    )


def test_evaluator_rejects_infinite_repeat_count():
    statements = [
        RepeatStatement(
            NumberLiteral(float("inf")), [SayStatement(StringLiteral("a"))], 1
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "repeat の回数は整数で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_nan_repeat_count():
    statements = [
        RepeatStatement(
            NumberLiteral(float("nan")), [SayStatement(StringLiteral("a"))], 1
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "repeat の回数は整数で書いてください" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")


def test_evaluator_rejects_overflowing_division():
    statements = [
        SayStatement(
            BinaryExpr(NumberLiteral(10**400), "/", NumberLiteral(2), 1)
        )
    ]

    try:
        Evaluator().evaluate(statements)
    except RuntimeError as error:
        assert "計算結果が大きすぎます" in str(error)
    else:
        raise AssertionError("RuntimeError was not raised")

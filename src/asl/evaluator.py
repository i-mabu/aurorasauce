from .ast import (
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


class Environment:
    """変数の置き場。名前と値の対応を覚える。"""

    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object, line: int) -> None:
        if name in self.values:
            raise RuntimeError(
                f"line {line}: 変数 '{name}' はすでに定義されています"
            )
        self.values[name] = value

    def assign(self, name: str, value: object, line: int) -> None:
        if name not in self.values:
            raise RuntimeError(
                f"line {line}: 変数 '{name}' は定義されていません"
            )
        self.values[name] = value

    def get(self, name: str, line: int) -> object:
        if name not in self.values:
            raise RuntimeError(
                f"line {line}: 変数 '{name}' は定義されていません"
            )
        return self.values[name]


class Evaluator:
    def __init__(self) -> None:
        self.env = Environment()

    def evaluate(self, statements: list[object]) -> None:
        for statement in statements:
            if isinstance(statement, SayStatement):
                print(f"AURORA: {self._format(self._eval(statement.expression))}")
                continue
            if isinstance(statement, AddStatement):
                self.env.define(
                    statement.name,
                    self._eval(statement.expression),
                    statement.line,
                )
                continue
            if isinstance(statement, AssignStatement):
                self.env.assign(
                    statement.name,
                    self._eval(statement.expression),
                    statement.line,
                )
                continue
            if isinstance(statement, IfStatement):
                self._eval_if(statement)
                continue
            if isinstance(statement, RepeatStatement):
                self._eval_repeat(statement)
                continue

            raise RuntimeError("unknown AST node")

    def _eval_repeat(self, statement: RepeatStatement) -> None:
        count = self._eval(statement.count)
        line = statement.line
        if isinstance(count, bool) or not isinstance(count, (int, float)):
            raise RuntimeError(
                f"line {line}: repeat の回数は数値で書いてください"
            )
        if isinstance(count, float) and not count.is_integer():
            # is_integer() は inf / nan でも例外にならず False を返す。
            # int(count) への変換は inf で OverflowError、nan で
            # ValueError になり、CLI のエラー境界をすり抜けていた。
            raise RuntimeError(
                f"line {line}: repeat の回数は整数で書いてください"
            )
        if count < 0:
            raise RuntimeError(
                f"line {line}: repeat の回数は 0 以上で書いてください"
            )
        for _ in range(int(count)):
            self.evaluate(statement.body)

    def _eval_if(self, statement: IfStatement) -> None:
        condition = self._eval(statement.condition)
        if not isinstance(condition, bool):
            raise RuntimeError(
                f"line {statement.line}: "
                "if の条件は true か false で書いてください"
            )
        if condition:
            self.evaluate(statement.then_branch)
        elif statement.else_branch is not None:
            self.evaluate(statement.else_branch)

    def _eval(self, expression: object) -> object:
        if isinstance(expression, StringLiteral):
            return expression.value
        if isinstance(expression, NumberLiteral):
            return expression.value
        if isinstance(expression, BoolLiteral):
            return expression.value
        if isinstance(expression, Identifier):
            return self.env.get(expression.name, expression.line)
        if isinstance(expression, BinaryExpr):
            return self._eval_binary(expression)

        raise RuntimeError("unknown AST node")

    def _eval_binary(self, expression: BinaryExpr) -> object:
        left = self._eval(expression.left)
        right = self._eval(expression.right)
        operator = expression.operator
        line = expression.line

        if operator == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._format(left) + self._format(right)
            return self._number_op(left, right, operator, line)

        if operator in ("==", "!="):
            # Python では bool が int のサブクラスのため、素の == では
            # 1 == true が真になってしまう。真偽値とそれ以外は別型として
            # 「等しくない」と扱う（他の演算での bool 排除と揃える）。
            if isinstance(left, bool) != isinstance(right, bool):
                return operator == "!="
            return left == right if operator == "==" else left != right

        if operator in ("<", "<=", ">", ">="):
            if isinstance(left, bool) or isinstance(right, bool):
                raise RuntimeError(f"line {line}: 比べられるのは数値だけです")
            if not isinstance(left, (int, float)) or not isinstance(
                right, (int, float)
            ):
                raise RuntimeError(f"line {line}: 比べられるのは数値だけです")
            if operator == "<":
                return left < right
            if operator == "<=":
                return left <= right
            if operator == ">":
                return left > right
            return left >= right

        return self._number_op(left, right, operator, line)

    def _number_op(
        self, left: object, right: object, operator: str, line: int
    ) -> int | float:
        if (
            isinstance(left, bool)
            or isinstance(right, bool)
            or not isinstance(left, (int, float))
            or not isinstance(right, (int, float))
        ):
            raise RuntimeError(f"line {line}: 計算できるのは数値だけです")
        try:
            if operator == "+":
                return left + right
            if operator == "-":
                return left - right
            if operator == "*":
                return left * right
            if operator == "/":
                if right == 0:
                    raise RuntimeError(
                        f"line {line}: 0 で割ることはできません"
                    )
                return left / right
        except OverflowError:
            # 巨大な整数と小数の混合演算や、巨大な整数同士の割り算は
            # float へ変換できず OverflowError になる。
            raise RuntimeError(
                f"line {line}: 計算結果が大きすぎます"
            ) from None

        raise RuntimeError(f"line {line}: 知らない演算子 '{operator}' です")

    @staticmethod
    def _format(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

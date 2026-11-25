# ==========================================
# 🌳 構文木ノード
# ==========================================

from dataclasses import dataclass


@dataclass(frozen=True)
class StringLiteral:
    value: str


@dataclass(frozen=True)
class NumberLiteral:
    value: int | float


@dataclass(frozen=True)
class BoolLiteral:
    value: bool


@dataclass(frozen=True)
class Identifier:
    name: str
    line: int


@dataclass(frozen=True)
class BinaryExpr:
    left: object
    operator: str
    right: object
    line: int


@dataclass(frozen=True)
class SayStatement:
    expression: object


@dataclass(frozen=True)
class AddStatement:
    name: str
    expression: object
    line: int


@dataclass(frozen=True)
class AssignStatement:
    name: str
    expression: object
    line: int


@dataclass(frozen=True)
class IfStatement:
    condition: object
    then_branch: list[object]
    else_branch: list[object] | None
    line: int


@dataclass(frozen=True)
class RepeatStatement:
    count: object
    body: list[object]
    line: int

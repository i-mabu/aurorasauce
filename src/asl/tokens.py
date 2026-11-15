from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    SAY = auto()
    ADD = auto()
    IF = auto()
    ELSE = auto()
    REPEAT = auto()
    TRUE = auto()
    FALSE = auto()
    STRING = auto()
    NUMBER = auto()
    IDENT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int

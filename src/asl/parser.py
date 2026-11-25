# ==========================================
# 🌳 構文解析
# ==========================================

import math

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
from .tokens import Token, TokenType

_COMPARISON_TOKENS = {
    TokenType.EQ,
    TokenType.NEQ,
    TokenType.LT,
    TokenType.LTE,
    TokenType.GT,
    TokenType.GTE,
}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[object]:
        statements: list[object] = []

        while not self._check(TokenType.EOF):
            statements.append(self._parse_statement())

        return statements

    def _parse_statement(self) -> object:
        if self._check(TokenType.SAY):
            return self._parse_say_statement()
        if self._check(TokenType.ADD):
            return self._parse_add_statement()
        if self._check(TokenType.IDENT):
            return self._parse_assign_statement()
        if self._check(TokenType.IF):
            return self._parse_if_statement()
        if self._check(TokenType.REPEAT):
            return self._parse_repeat_statement()

        token = self.tokens[self.current]
        raise SyntaxError(
            f"line {token.line}: 文は say / add / 代入 / if / repeat から始めてください"
        )

    def _parse_say_statement(self) -> SayStatement:
        self._consume(TokenType.SAY, "say の後に式が必要です")
        expression = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "';' が必要です")

        return SayStatement(expression)

    def _parse_add_statement(self) -> AddStatement:
        add_token = self._consume(TokenType.ADD, "add の後に変数名が必要です")
        name_token = self._consume(
            TokenType.IDENT, "add の後に変数名が必要です"
        )
        self._consume(TokenType.ASSIGN, "変数名の後に '=' が必要です")
        expression = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "';' が必要です")

        return AddStatement(name_token.lexeme, expression, add_token.line)

    def _parse_assign_statement(self) -> AssignStatement:
        name_token = self._consume(
            TokenType.IDENT, "代入には変数名が必要です"
        )
        self._consume(TokenType.ASSIGN, "変数名の後に '=' が必要です")
        expression = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "';' が必要です")

        return AssignStatement(name_token.lexeme, expression, name_token.line)

    def _parse_if_statement(self) -> IfStatement:
        if_token = self._consume(TokenType.IF, "if の後に条件が必要です")
        condition = self._parse_expression()
        self._consume(TokenType.LBRACE, "条件の後に '{' が必要です")
        then_branch = self._parse_block()
        else_branch = None
        if self._check(TokenType.ELSE):
            self._advance()
            self._consume(TokenType.LBRACE, "else の後に '{' が必要です")
            else_branch = self._parse_block()

        return IfStatement(condition, then_branch, else_branch, if_token.line)

    def _parse_repeat_statement(self) -> RepeatStatement:
        repeat_token = self._consume(
            TokenType.REPEAT, "repeat の後に回数が必要です"
        )
        count = self._parse_expression()
        self._consume(TokenType.LBRACE, "回数の後に '{' が必要です")
        body = self._parse_block()

        return RepeatStatement(count, body, repeat_token.line)

    def _parse_block(self) -> list[object]:
        statements: list[object] = []

        while not self._check(TokenType.RBRACE):
            if self._check(TokenType.EOF):
                token = self.tokens[self.current]
                raise SyntaxError(f"line {token.line}: '}}' が必要です")
            statements.append(self._parse_statement())

        self._consume(TokenType.RBRACE, "'}' が必要です")
        return statements

    def _parse_expression(self) -> object:
        return self._parse_comparison()

    def _parse_comparison(self) -> object:
        left = self._parse_additive()

        while self.tokens[self.current].type in _COMPARISON_TOKENS:
            operator = self._advance()
            right = self._parse_additive()
            left = BinaryExpr(left, operator.lexeme, right, operator.line)

        return left

    def _parse_additive(self) -> object:
        left = self._parse_multiplicative()

        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            operator = self._advance()
            right = self._parse_multiplicative()
            left = BinaryExpr(left, operator.lexeme, right, operator.line)

        return left

    def _parse_multiplicative(self) -> object:
        left = self._parse_factor()

        while self._check(TokenType.STAR) or self._check(TokenType.SLASH):
            operator = self._advance()
            right = self._parse_factor()
            left = BinaryExpr(left, operator.lexeme, right, operator.line)

        return left

    def _parse_factor(self) -> object:
        if self._check(TokenType.MINUS):
            operator = self._advance()
            # 📌 単項マイナスは 0 から引く形に直す（例：-3 は 0 - 3）。
            operand = self._parse_factor()
            return BinaryExpr(
                NumberLiteral(0), "-", operand, operator.line
            )

        if self._check(TokenType.NUMBER):
            token = self._advance()
            try:
                value: int | float = (
                    float(token.lexeme)
                    if "." in token.lexeme
                    else int(token.lexeme)
                )
            except ValueError:
                # 🔢 桁数が Python の変換上限を超えるリテラルなど。
                raise SyntaxError(
                    f"line {token.line}: 数値が大きすぎます"
                ) from None
            if isinstance(value, float) and not math.isfinite(value):
                # 🔢 巨大な小数リテラルが inf に化けるのを防ぐ。
                raise SyntaxError(f"line {token.line}: 数値が大きすぎます")
            return NumberLiteral(value)

        if self._check(TokenType.STRING):
            token = self._advance()
            return StringLiteral(token.lexeme)

        if self._check(TokenType.TRUE):
            self._advance()
            return BoolLiteral(True)

        if self._check(TokenType.FALSE):
            self._advance()
            return BoolLiteral(False)

        if self._check(TokenType.IDENT):
            token = self._advance()
            return Identifier(token.lexeme, token.line)

        if self._check(TokenType.LPAREN):
            self._advance()
            expression = self._parse_expression()
            self._consume(TokenType.RPAREN, "')' が必要です")
            return expression

        token = self.tokens[self.current]
        raise SyntaxError(f"line {token.line}: 式が必要です")

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()

        token = self.tokens[self.current]
        raise SyntaxError(f"line {token.line}: {message}")

    def _advance(self) -> Token:
        token = self.tokens[self.current]
        self.current += 1
        return token

    def _check(self, token_type: TokenType) -> bool:
        return self.tokens[self.current].type == token_type

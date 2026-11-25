# ==========================================
# ✂️ 字句解析
# ==========================================

from .tokens import Token, TokenType


def _is_digit(char: str) -> bool:
    # 🔢 数値リテラルは ASCII の数字だけにする。str.isdigit() は '²' など
    # int()/float() で変換できない文字も数字と判定してしまうため。
    return "0" <= char <= "9"

_SINGLE_CHAR_TOKENS = {
    ";": TokenType.SEMICOLON,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "=": TokenType.ASSIGN,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
}

_TWO_CHAR_TOKENS = {
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LTE,
    ">=": TokenType.GTE,
}

_KEYWORDS = {
    "say": TokenType.SAY,
    "add": TokenType.ADD,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "repeat": TokenType.REPEAT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.current = 0
        self.line = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self.current < len(self.source):
            char = self.source[self.current]

            if char.isspace():
                if char == "\n":
                    self.line += 1
                self.current += 1
                continue

            if char == "#":
                self._skip_comment()
                continue

            if char in "<>=!":
                two = self.source[self.current:self.current + 2]
                if two in _TWO_CHAR_TOKENS:
                    tokens.append(Token(_TWO_CHAR_TOKENS[two], two, self.line))
                    self.current += 2
                    continue
                if char in _SINGLE_CHAR_TOKENS:
                    tokens.append(
                        Token(_SINGLE_CHAR_TOKENS[char], char, self.line)
                    )
                    self.current += 1
                    continue
                raise SyntaxError(
                    f"line {self.line}: 使えない文字 '{char}' があります"
                )

            if char in _SINGLE_CHAR_TOKENS:
                tokens.append(
                    Token(_SINGLE_CHAR_TOKENS[char], char, self.line)
                )
                self.current += 1
                continue

            if char == '"':
                tokens.append(self._read_string())
                continue

            if _is_digit(char):
                tokens.append(self._read_number())
                continue

            if char.isalpha() or char == "_":
                word = self._read_word()
                token_type = _KEYWORDS.get(word, TokenType.IDENT)
                tokens.append(Token(token_type, word, self.line))
                continue

            raise SyntaxError(
                f"line {self.line}: 使えない文字 '{char}' があります"
            )

        tokens.append(Token(TokenType.EOF, "", self.line))
        return tokens

    def _skip_comment(self) -> None:
        while self.current < len(self.source):
            if self.source[self.current] == "\n":
                return
            self.current += 1

    def _read_word(self) -> str:
        start = self.current

        while self.current < len(self.source):
            char = self.source[self.current]
            if not (char.isalnum() or char == "_"):
                break
            self.current += 1

        return self.source[start:self.current]

    def _read_number(self) -> Token:
        start = self.current

        while self.current < len(self.source):
            if not _is_digit(self.source[self.current]):
                break
            self.current += 1

        if (
            self.current + 1 < len(self.source)
            and self.source[self.current] == "."
            and _is_digit(self.source[self.current + 1])
        ):
            self.current += 1
            while self.current < len(self.source):
                if not _is_digit(self.source[self.current]):
                    break
                self.current += 1

        return Token(
            TokenType.NUMBER, self.source[start:self.current], self.line
        )

    def _read_string(self) -> Token:
        self.current += 1
        start = self.current

        while self.current < len(self.source):
            char = self.source[self.current]

            if char == '"':
                value = self.source[start:self.current]
                self.current += 1
                return Token(TokenType.STRING, value, self.line)

            if char == "\n":
                self.line += 1

            self.current += 1

        raise SyntaxError(f"line {self.line}: unterminated string")

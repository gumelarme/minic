from minic.scanner import Scanner, Token

class SyntaxError(Exception):
    """Syntactically error exception."""
    def __init__(self, scanner: Scanner, token: Token, message, errors=None):
        self._message = message
        self.scanner = scanner
        self.token = token
        self.errors = errors

        super(SyntaxError, self).__init__(self.message)

    @property
    def message(self):
        return self.getMessage()

    @message.setter
    def message(self, message):
        """Generate new message with code block for the exception"""
        self._message = message
        super(SyntaxError, self).__init__(self.message)

    def getMessage(self):
        return "{}, [{}:{}]\n{}".format(
            self._message,
            self.token.linum,
            self.scanner.filename,
            self.scanner.spit(self.token.linum, 1),
        )

from minic.scanner import Scanner, Token

class SemanticError(Exception):
    """Semantically error exception."""
    def __init__(self, node, scope, message, errors=None):
        self.message = message
        self.node = node
        self.scope = scope
        self.errors = errors
        super(SemanticError, self).__init__(self.getMessage())


    def getMessage(self):
        return "{}, [{}:{}]".format(
            self.message,
            self.node.linum,
            self.scope.name
        )



class DatabaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InternalError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ExternalError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ExternalValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InternalValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

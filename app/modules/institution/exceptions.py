class UserAlreadyExistsError(Exception):
    """Raised when there's already an account created with the e-mail informed"""
    pass

class CoordinatorDoesntExistError(Exception):
    """Raised when coordinator_id informed on professor creation doesn't exist or isn't a coordinator"""
    pass

class InstitutionDoesntExistError(Exception):
    """Raised when institution_id does not represent any institution"""
    pass

class EmailDomainNotAllowedError(Exception):
    """Raised when the e-mail domain isn't registered for the institution"""
    pass

class ProbabilityError(Exception):
    pass


class ProbabilityRangeError(ProbabilityError):
    pass


class ProbabilityTypeError(ProbabilityError):
    pass


class NumError(ProbabilityError):
    pass


class NotGivenValueError(ProbabilityError):
    pass


class NotUsedError(ProbabilityError):
    pass


class ImmutableConstantVariableError(ProbabilityError):
    pass


class ConstantError(ProbabilityError):
    pass


class InvalidParameterValue(ProbabilityError):
    pass

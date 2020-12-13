# We create our own copy of ValidationError, so we don't expose
# import dependency on pydantic. However, pydantic is doing
# an extremely good job providing error message, so we will
# feed them to our exception.
# https://github.com/samuelcolvin/pydantic/blob/master/pydantic/error_wrappers.py#L59-L65
class ValidationError(ValueError):
    # pylint: disable=super-init-not-called
    def __init__(self, msg):
        self.msg = msg

def require_connection(func):
    """Wrapper which ensures that the adapter is connected.

    In order to use it, place @require_connection above your function definition.
    As long as the adapter is connected, the function is ran normally.
    If the adapter is not connected, an exception is raised.

    """

    def wrapper(self, *args, **kwargs):
        if not self.is_connected():
            raise RuntimeError(
                f"{self.__class__.__name__} is not connected. Please call 'connect' before using this method."
            )
        return func(self, *args, **kwargs)

    return wrapper

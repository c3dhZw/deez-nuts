class APIError(Exception):
    pass


class UserError(Exception):
    def __init__(self, *args, json=None, **kwargs) -> None:
        self.json = json
        super().__init__(*args, **kwargs)

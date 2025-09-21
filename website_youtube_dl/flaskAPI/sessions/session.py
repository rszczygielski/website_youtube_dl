class SessionClient():

    def __init__(self, session):
        self.session = session

    def add_elem_to_session(self, key, value):
        self.session[key] = value

    def delete_elem_form_session(self, key):
        if not self.if_elem_in_session(key):
            return
        self.session.pop(key)

    def if_elem_in_session(self, key):
        if key not in self.session.keys():
            app.logger.error(f"Session doesn't have a key: {key}")
            return False
        return True

    def get_session_elem(self, key):
        if not self.if_elem_in_session(key):
            return
        return self.session[key]

    def print_session_keys(self):  # pragma: no_cover
        app.logger.info(self.session.keys())

    def clear_session(self):  # pragma: no_cover
        self.session.clear()

    def get_all_session_keys(self):  # pragma: no_cover
        return self.session.keys()

    def __del__(self):
        self.clear_session()

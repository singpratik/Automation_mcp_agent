class SessionMemory:
    """
    Persistent memory for a browser automation session.
    Stores selectors, actions, results, and errors for adaptive, stateful automation.
    """
    def __init__(self):
        self.elements = {}  # {element_name: selector/xpath/id}
        self.actions = []   # List of (action, params, result, error)
        self.last_error = None
        self.last_result = None
        self.cookies = None
        self.current_url = None

    def store_element(self, name, selector):
        self.elements[name] = selector

    def get_element(self, name):
        return self.elements.get(name)

    def log_action(self, action, params, result=None, error=None):
        self.actions.append({
            "action": action,
            "params": params,
            "result": result,
            "error": error
        })
        if error:
            self.last_error = error
        if result:
            self.last_result = result

    def clear_error(self):
        self.last_error = None

    def set_cookies(self, cookies):
        self.cookies = cookies

    def set_url(self, url):
        self.current_url = url

    def get_last_action(self):
        return self.actions[-1] if self.actions else None

    def get_last_error(self):
        return self.last_error

    def get_last_result(self):
        return self.last_result

    def reset(self):
        self.elements = {}
        self.actions = []
        self.last_error = None
        self.last_result = None
        self.cookies = None
        self.current_url = None

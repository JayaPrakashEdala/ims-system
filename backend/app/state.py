class State:
    def next(self):
        return None


class OpenState(State):
    def next(self):
        return "INVESTIGATING"


class InvestigatingState(State):
    def next(self):
        return "RESOLVED"


class ResolvedState(State):
    def next(self):
        return "CLOSED"


def get_next_state(current_state):
    if current_state == "OPEN":
        return OpenState().next()
    elif current_state == "INVESTIGATING":
        return InvestigatingState().next()
    elif current_state == "RESOLVED":
        return ResolvedState().next()
    return current_state

class AlertStrategy:
    def get_severity(self):
        return "P3"


class RDBMSAlert(AlertStrategy):
    def get_severity(self):
        return "P0"


class CacheAlert(AlertStrategy):
    def get_severity(self):
        return "P2"


def get_alert_strategy(component_id: str):
    comp = component_id.upper()  # ✅ fix

    if "RDBMS" in comp:
        return RDBMSAlert()
    elif "CACHE" in comp:
        return CacheAlert()
    return AlertStrategy()
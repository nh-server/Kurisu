class Module:
    """
    Describes a Module. A Module contains a dictionary of ResultCodes,
    and possibly a second dictionary with extra information.
    A module itself is basically who raised the error or returned the result.
    """
    def __init__(self, name, data={}, levels={}):
        self.name = name
        self.data = data
        self.levels = levels

    def get_error(self, error: int):
        for key, value in self.data.items():
            if key == error:
                return value
            elif isinstance(key, tuple) and key[0] <= error <= key[1]:
                return value

        return UNKNOWN_ERROR

    # If your modules require specific extra info for error ranges, add it here
    def get_level(self, level: int):
        for key, value in self.levels.items():
            if isinstance(key, tuple) and key[0] <= level <= key[1]:
                return value
        return None


class ResultInfo:
    """
    Holds information on a result or support code. A ResultInfo has several fields which are used
    to provide information about the result, error, or support code, including a support
    webpage, if available.
    """
    def __init__(self, description='', support_url='', is_ban=False):
        self.description = description
        self.support_url = support_url
        self.summary = None
        self.level = None
        self.is_ban = is_ban
        self.is_support = False


# Helper constants
REPORT_DETAILS = 'You should report relevant details to \
[the Kurisu repository](https://github.com/nh-server/Kurisu/issues).'

UNKNOWN_MODULE = ResultInfo(f'Invalid or unknown module. Are you sure you \
typed the error code in correctly? {REPORT_DETAILS}')

UNKNOWN_ERROR = ResultInfo(f'Your error appears to be unknown. {REPORT_DETAILS}')

NO_RESULTS_FOUND = ResultInfo(f'I know about this module, but I don\'t have any \
information on error codes for it. {REPORT_DETAILS}')

WARNING_COLOR = 0xFFFF00

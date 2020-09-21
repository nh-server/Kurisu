class Module():
    def __init__(self, name, data={}, levels={}):
        self.name = name
        self.data = data
        self.levels = levels

    def get_error(self, error:int):
        for key, value in self.data.items():
            if key == error:
                return value
            elif isinstance(key, tuple) and key[0] <= error <= key[1]:
                return value

        return UNKNOWN_ERROR

    # Wii U and Switch-specific
    def get_level(self, level:int):
        for key, value in self.levels.items():
            if isinstance(key, tuple) and key[0] <= level <= key[1]:
                return value
        return None

class ResultCode():
    def __init__(self, description=None, support_url=None):
        self.description = description
        self.support_url = support_url
        self.summary = None
        self.level = None
        self.code = None

UNKNOWN_MODULE =  ResultCode('Invalid or unknown module. Are you sure you \
typed the error code in correctly?')

UNKNOWN_ERROR = ResultCode('Your error appears to be unknown. You should report\
 relevant details to \
[the Kurisu repository](https://github.com/nh-server/Kurisu/issues).')

NO_RESULTS_FOUND = ResultCode('I know about this module, but I don\'t have any \
information on error codes for it. You should report relevant details to \
[the Kurisu repository](https://github.com/nh-server/Kurisu/issues).')

WARNING_COLOR = 0xFFFF00


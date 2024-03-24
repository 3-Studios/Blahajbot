from discord.app_commands import AppCommandError

class BlahajBotError(AppCommandError):
    pass

# Exceptions applicable to most commands
class NoBlahaj(BlahajBotError):
    pass
class NoBlahajSelf(NoBlahaj):
    pass
class NoBlahajOthers(NoBlahaj):
    pass
class InvalidAmount(BlahajBotError):
    pass
class InvalidItem(BlahajBotError):
    pass
class TooLittleOfItem(InvalidAmount):
    pass

# Exceptions that are used across a small number of commands
class InvalidFood(InvalidItem):
    pass
class TooLittleOfFood(TooLittleOfItem):
    pass

# Very niche exceptions
class AlreadyHaveBlahaj(BlahajBotError):
    pass
class NameTooLong(BlahajBotError):
    pass


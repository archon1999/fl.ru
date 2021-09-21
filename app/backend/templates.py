from .models import Template


keys = Template.keys.all()
messages = Template.messages.all()
smiles = Template.smiles.all()


class Keys():
    PROJECTS = keys[0]
    SETTINGS = keys[1]
    MENU = keys[2]
    CANCEL = keys[3]
    NOTIFICATIONS = keys[4]
    ON = keys[5]
    OFF = keys[6]
    BUDGET_MIN = keys[7]
    BUDGET_MAX = keys[8]
    SAFE_DEAL = keys[9]
    CHAPTERS = keys[10]
    BACK = keys[11]
    NOT_INDICATED = keys[12]
    KEYWORDS = keys[13]
    RESET = keys[14]
    SELECT_ALL = keys[15]


class Messages():
    PROJECT = messages[0]
    ENTER = messages[1]
    CANCELED = messages[2]
    FILTER_BUDGET_INCORRECT_INPUT = messages[3]
    SAVED = messages[4]


class Smiles():
    ON = smiles[0]
    OFF = smiles[1]

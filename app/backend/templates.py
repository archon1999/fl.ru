from .models import Template


keys = Template.keys.all()
messages = Template.messages.all()
smiles = Template.smiles.all()


class Keys():
    KEY = keys[0]


class Messages():
    PROJECT = messages[0]


class Smiles():
    SMILE = smiles[0]

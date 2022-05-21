from mycroft import MycroftSkill, intent_file_handler


class Tmp(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('tmp.intent')
    def handle_tmp(self, message):
        self.speak_dialog('tmp')


def create_skill():
    return Tmp()


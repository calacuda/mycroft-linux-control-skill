from adapt.tools.text.tokenizer import EnglishTokenizer
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler
import socket
from subprocess import Popen, PIPE
import sockets

def to_api(cmd):
    """replaces spaces with null chars and trurns it to bytes"""
    null = bytes(chr(0), 'utf-8')
    return b''.join([bytes(tok, 'utf-8') + null for tok in cmd.split(' ')])


def send(spath, payload):
    """send payload over the unix socket"""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(spath)
        s.send(to_api(payload))
        s.shutdown(1)
        res = s.recv(1024)
        # print(str(res))
        return res


class LinuxControl(MycroftSkill):
    def __init__(self):
        super().__init__(self)
        self.api_path = ""
        self.desktops = []

    def initialize(self):
        self.api_path = self.settings.get('api-socket', "/tmp/desktop-automater")
        self.bspwm_path = self.settings.get('bspwm-socket', "/tmp/bspwm_0_0-socket")
        self.get_desktops()

    def stop(self):
        pass

    def get_desktops(self):
        "bspc query -D --names"
        desktops = run(
                        ["bspc", "query", "-D", "--names"],
                        stdout=PIPE,
                        stderr=PIPE
                      ).stdout.decode('utf-8')
        if desktops:
            for desktop in desktops.split("\n"):
                if desktop:
                    self.desktops.append(desktop)
                    self.register_vocabulary(desktop, 'Desktop')

    def api_send(self, payload, success_f, failed_f):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(self.api_path)
            s.send(bytes(payload, 'ascii'))
            s.shutdown(1)  # tells the server im done sending data and it can reply now.
            if int(s.recv(1024)[0].decode('utf-8')[0]) == 0:
                # success
                # have it beep instead of say things if success_f is 'blank'
                self.speak_dialog(success_f)
                return True
            else:
                # failed
                # have it beep instead of say things if failed_f is 'blank'
                self.speak_dialog(failed_f)
                return False


    def query_wrap(self, query):
        return send(self.bspwm_path, f"query {payload}").decode('utf-8')

    @intent_handler(IntentBuilder('lock'))
    def handle_lock(self, message):
        return self.api_send("lock", 'lock-success', 'lock-failed')

    @intent_handler(IntentBuilder('sleep'))
    def handle_sleep(self, message):
        return self.api_send("speep", 'blank', 'sleep-failed')

    @intent_handler(IntentBuilder('hibernate'))
    def handle_hibernate(self, message):
        return self.api_send("hibernate", 'blank', 'hibernate-failed')

    @intent_handler(IntentBuilder('switch-desktops').require('Desktop'))
    def handle_switch_desktops(self, message):
        desktop = message.data.get('Desktop')
        return self.api_send(f"focus-on {desktop}", 'blank', 'blank')

    @intent_handler(IntentBuilder('move').require('Desktop'))
    def handle_move(self, message):
        desktop = message.data.get('Desktop')
        return self.api_send(f"move-to {desktop}", 'blank', 'move-failed')


def create_skill():
    return LinuxControl()

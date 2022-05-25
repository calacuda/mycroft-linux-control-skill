from adapt.tools.text.tokenizer import EnglishTokenizer
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler
import socket
from subprocess import run, PIPE
import sockets
from os import listdir
from os.path import isfile, expanduser, basename
from pathlib import Path



def to_api(cmd):
    """replaces spaces with null chars and trurns it to bytes"""
    null = bytes(chr(0), 'utf-8')
    return b''.join([bytes(str(tok), 'utf-8') + null for tok in cmd.split(' ')])


def bspwm_send(spath, payload):
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
        super().__init__()
        self.api_path = ""
        self.bspwm_path = ""
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
        self.log.debug(f"DESKTOPS: {self.desktops}")

    def api_send(self, payload, success_f, failed_f):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(self.api_path)
            s.send(bytes(payload, 'ascii'))
            s.shutdown(1)  # tells the server im done sending data and it can reply now.
            res = s.recv(1024).decode('utf-8')
            if int(res[0]) == 0:
                # success
                # have it beep instead of say things if success_f is 'blank'
                if success_f:
                    self.speak_dialog(success_f)
                return True
            else:
                # failed
                # have it beep instead of say things if failed_f is 'blank'
                if failed_f:
                    self.speak_dialog(failed_f)
                return False


    def query_wrap(self, query):
        return bspwm_send(self.bspwm_path, f"query {payload}").decode('utf-8')

    @intent_handler(IntentBuilder('LockIntent').require('lock'))
    def handle_lock(self, message):
        return self.api_send("lock", 'lock-success', 'lock-failed')

    @intent_handler(IntentBuilder('SleepIntent').require('sleep'))
    def handle_sleep(self, message):
        return self.api_send("sleep", '', 'sleep-failed')

    @intent_handler(IntentBuilder('HibernateIntent').require('hibernate'))
    def handle_hibernate(self, message):
        return self.api_send("hibernate", '', 'hibernate-failed')

    @intent_handler(IntentBuilder('SwitchDesktops')
                    .require('switch-desktops')
                    .require('Desktop'))
    def handle_switch_desktops(self, message):
        desktop = message.data.get('Desktop')
        return self.api_send(f"focus-on {desktop}", '', '')

    @intent_handler(IntentBuilder('MoveDesktops')
                    .require('move-to')
                    .require('Desktop'))
    def handle_move(self, message):
        desktop = message.data.get('Desktop')
        return self.api_send(f"move-to {desktop}", '', 'move-failed')

    @intent_handler("layout.intent")
    def handle_load_layout(self, message):
        # self.log.warning("setting layout")
        layout = message.data.get('layout')#.replace(" ", "-")
        tokenizer = EnglishTokenizer()
        processed_layout = layout.lower()
        self.log.warning(f"loading layout {layout}")
        for f in listdir(expanduser("~/.config/desktop-automater/layouts/")):
            f_basename = ".".join(basename(f).split(".")[:-1])
            self.log.warning(f"looking at file {f_basename}")
            if Path(f).is_file() and f_basename.lower() == processed_layout:
                layout = layout.replace(" ", "-")
                self.speak_dialog(f"configuring layout {layout}")
                return self.api_send(f"load-layout {f_basename}", "layout-load-success", "layout-load-failed")

        self.speak_dialog(
        f"could not find {layout}, make sure the layout or yaml file is named correctly, and in the right directory. layout file {layout}"
        )
        return False


def create_skill():
    return LinuxControl()

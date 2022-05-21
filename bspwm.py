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

import os, socket

# if it is not set, it will try to find the router ip. if /etc/hosts is set it might grab the local computers ip instead
def get_envvars_routerip():
    try:
        return os.environ.get('DECOUVRIR_ROUTER_IP')
    except Exception as e:
        print ('Router IP environment variable not set, will try to find the router IP: ' + e)
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("192.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

def get_envvars_routerUser():
    try:
        return os.environ.get('DECOUVRIR_ROUTER_USER')
    except Exception as e:
        print ('Router username environment variable not set, setting default of "username": ' + e)
        return "username"

def get_envvars_routerPass():
    try:
        return os.environ.get('DECOUVRIR_ROUTER_PASS')
    except Exception as e:
        print ('Router password environment variable not set, setting default of "password": ' + e)
        return "password"
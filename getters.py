import os, socket

# if it is not set, it will try to find the router ip. if /etc/hosts is set it might grab the local computers ip instead
def get_envvars_routerip():
    try:
        return os.environ.get('DECOUVRIR_ROUTER_IP')
    except Exception as e:
        return 'Router IP environment variable not set, will try to find the router IP: ', e
    # I dont know why I put this line here... Commenting out as I can't remember as of right now. 2/15/2020
    #return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("192.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

def get_envvars_routerUser():
    try:
        return os.environ.get('DECOUVRIR_ROUTER_USER')
    except Exception as e:
        return 'Router username environment variable not set, setting default of "username": ', e

def get_envvars_routerPass():
    try:
        return os.environ.get('DECOUVRIR_ROUTER_PASS')
    except Exception as e:
        return 'Router password environment variable not set, setting default of "password": ', e

def get_envvars_mysql_host():
    try:
        return os.environ.get('DECOUVRIR_MYSQL_HOST')
    except Exception as e:
        return 'No MySQL host defined: ', e

def get_envvars_mysql_user():
    try:
        return os.environ.get('DECOUVRIR_MYSQL_USER')
    except Exception as e:
        return 'No MySQL user defined: ', e

def get_envvars_mysql_pass():
    try:
        return os.environ.get('DECOUVRIR_MYSQL_PASS')
    except Exception as e:
        return 'No MySQL user defined: ', e

def get_envvars_mysql_db():
    try:
        return os.environ.get('DECOUVRIR_MYSQL_DB')
    except Exception as e:
        return 'No MySQL user defined: ', e
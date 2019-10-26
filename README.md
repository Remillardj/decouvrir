# decouvrir
A simple flask web server to view the IP's and hostnames of my local network. Can be run on a tiny linux box instead of having to log into your router and query for a specific device or memorize them.

## Setup
- make sure you have flask installed
- make sure you are running Python 3.7.x which is what this was built on, no guarantees of compatibility
- run `pip3 install -r requirments.txt`

## How to run
- make sure python packages (paramiko, flaskd, dnspython, nmap) are installed using pip, program was written for python 3.7
- `nohup python3.7 app.py > /var/log/flask.log 2>&1` to run in the backlog
- or simply `python3.7 app.py` to get it up and running

## Known Bugs
1. If you don't export environment variables, it'll appear that its unable to connect to the EdgeOS router. My logic in the getter.py for some reason aren't working.
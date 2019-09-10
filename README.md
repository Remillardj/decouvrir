# decouvrir
A simple flask web server to view the IP's and hostnames of my local network. Can be run on a tiny linux box instead of having to log into your router and query for a specific device or memorize them.


## How to run
- make sure python packages (paramiko, flask) are installed using pip, program was written for python 3.7
- `nohup python3.7 app.py > /var/log/flask.log 2>&1` to run in the backlog

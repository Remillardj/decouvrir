from flask import Flask, render_template_string
app = Flask(__name__)

import paramiko
import socket
import datetime


#
# Author: Jaryd Remillard
# Date: 9/10/2019
# Notes: Keep in mind this is just a tool I use locally, not meant for production
# Version: 0.0.1
# https://github.com/Remillardj
#


# Use paramiko to ssh into the server and grab hostnames and ip's, return output
# Function taken from LANDiscover repo
def edgeos_get_dhcp_leases(server, username, password, output={}, hostname="vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $6}'", port=22):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, username=username, password=password)
        output = {}
        hostnames = []
        (stdin, stdout, stderr) = client.exec_command(hostname)
        for line in stdout.readlines():
            if (line != "?\n"):
                hostnames.append(line.rstrip())
        client.close()
        for item in hostnames:
            output[item] = socket.gethostbyname(item)
        return output
    except Exception as e:
        print("Failed to connect to EdgeOS Router:", e)

# Prettify JSON output from Hostname, IP values
# Puts them into a table with no border
# output is a dictionary (key/value) from the router
def prettify_json():
	devices = edgeos_get_dhcp_leases(<ROUTER IP>, <ROUTER USERNAME>, <ROUTER PASSWORD>, output={}, hostname="vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $6}'", port=22)
	return render_template_string('''
		<table border="1">
			<tr>
				<td>Hostname</td>
				<td>IP</td>
			</tr>
			{% for hostname, ip in devices.items() %}
				<tr>
					<td>{{ hostname }}</td>
					<td>{{ ip }}</td>
				</tr>
			{% endfor %}
		</table>
		''', devices=devices)

@app.route("/")
def show_devices():
	now = datetime.datetime.now()
	showOutput = "<meta http-equiv='refresh' content='5'><title>Discouvrir</title>{}<br><br>Last Update: {}".format(prettify_json(), now)
	return showOutput


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')
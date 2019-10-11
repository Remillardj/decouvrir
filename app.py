from flask import Flask, render_template
app = Flask(__name__)

import paramiko
import socket
import datetime
import nmap
import getters

#
# Author: Jaryd Remillard
# Date: 9/10/2019
# Notes: Keep in mind this is just a tool I use locally, not meant for production
# Version: 0.0.2
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
        exit(1)

# dictionary values
def get_values(keyValue):
    output = []
    for k, v in keyValue.items():
        output.append(v)
    return output

# returns list with tuple for each item
# tuple is (ip, status)
def get_status_nmap(ip):
    nm = nmap.PortScanner()
    ip = ip + "/24"
    nm.scan(ip, arguments='-n -sP -PE -PA20,21,23,80,443,3306,3389')
    return [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

# Prettify JSON output from Hostname, IP values
# Puts them into a table with no border
# output is a dictionary (key/value) from the router
def prettify_json(devices):
    values = get_values(devices)
    status = get_status_nmap('192.168.50.0')
    return merge_device_status(devices, status)

def resolve_ip(ip):
    name, alias, addresslist = socket.gethostbyaddr(ip)
    return (name)

# status is dict in form of ip = status
# device is output from edgeos_get_dhcp_leases method
# compares IP, if matching then combine into dictionary
# output values is list of devices IP and status if up or down
def merge_device_status(device, status):
    output = {}
    for deviceName, deviceIp in device.items():
        output[deviceName] = [deviceIp, 'DOWN']
        for statusIp, statusStatus in status:
            if (deviceIp == statusIp):
                output[deviceName] = [deviceIp, statusStatus.upper()]
    return output

# Args: N/A
# Output: Date time in DD-MM-YY HH:SS:MM
def now():
    return datetime.datetime.now()

@app.route("/")
def show_devices():
    routerIp = getters.get_envvars_routerip()
    routerUser = getters.get_envvars_routerUser()
    routerPass = getters.get_envvars_routerPass()

    getDevices = edgeos_get_dhcp_leases(routerIp, routerUser, routerPass, output={}, hostname="vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $6}'", port=22)
    prettifyDevices = prettify_json(getDevices)
    return render_template("index.html", devices=prettifyDevices, lastUpdate=now())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')
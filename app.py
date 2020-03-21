from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import paramiko
import socket
import datetime
import nmap
import pymysql
import threading

# internal file
import getters

#
# Author: Jaryd Remillard
# Date: 9/10/2019
# Notes: Keep in mind this is just a tool I use locally, not meant for production
# Updated: 10/26/2019
# Version: 0.0.3
# https://github.com/Remillardj
#

# create connection to database
db = None
cursor = None
try:
    db = pymysql.connect(getters.get_envvars_mysql_host(), getters.get_envvars_mysql_user(),getters.get_envvars_mysql_pass(), getters.get_envvars_mysql_db())
    cursor = db.cursor()
except Exception as e:
    print("Error connecting to database: ", e)

def create_database_if_exists():
    cursor.execute("""
    CREATE DATABASE IF NOT EXISTS 'decouvrir';
    """)
    db.commit()

'''
 Input:
    - existing database connection -> cursor
    - table name to check -> table

 Returns:
     Boolean
'''
def check_if_table_created(table):
    cursor.execute("""
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_name='{}';
    """).format(table)
    if (cursor.fetchone()[0] == 1):
        return True
    return False

def create_table_if_exists():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `devices` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `ip` VARCHAR(255),
        `hostname` VARCHAR(255),
        `first_seen` TIMESTAMP DEFAULT '1970-01-01 00:00:01',
        `updated_at` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP DEFAULT '1970-01-01 00:00:01',
        `last_status` VARCHAR(255),
        KEY `ip` (`ip`) USING BTREE,
        KEY `hostname` (`hostname`) USING BTREE,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB;
    """)
    db.commit()
create_table_if_exists()

def insert_into_table(query):
    try:
        cursor.execute(query)
        db.commit()
    except Exception as e:
        return e

def check_if_exists_with_id(id):
    try:
        result = cursor.execute("""
        SELECT COUNT(*) FROM devices WHERE id='{0}'
        """).format(id)
        if (result.fetchone()[0] == 1):
            return result
        return False
    except Exception as e:
        return e

def check_if_exists_with_ip(ip):
    try:
        result = cursor.execute("""
        SELECT COUNT(*) FROM devices WHERE ip='{0}'
        """).format(ip)
        if (result.fetchone()[0] == 1):
            return result
        return False
    except Exception as e:
        return e

def check_if_exists_with_hostname(hostname):
    try:
        result = cursor.execute("""
        SELECT COUNT(*) FROM devices WHERE ip='{0}'
        """).format(hostname)
        if (result.fetchone()[0] == 1):
            return result
        return False
    except Exception as e:
        return e

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
        return "Failed to connect to EdgeOS Router:", e

# query the router and return a list from the output
def edgeos_vbash_runner(vbash):
    try:
        client = paramiko.SSHClient()
        client.set_miss_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(getters.get_envvars_routerip(), "22", getters.get_envvars_routerUser(), getters.get_envvars_routerPass())
        output = []
        (stdin, stdout, stderr) = client.exec_command(vbash)
        for line in stdout.readlines():
            if (line != "?\n"):
                output.append(line.rstrip())
            client.close()
        return output
    except Exception as e:
        return "Unable to query router: ", e

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

def get_single_status_nmap(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-n -sP -PE -PA20,21,23,80,443,3306,3389')
    return [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

def get_ip_status(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-sn')
    return [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

# Prettify JSON output from Hostname, IP values
# Puts them into a table with no border
# output is a dictionary (key/value) from the router
def prettify_json(devices):
    status = get_status_nmap('192.168.50.0')
    return merge_device_status(devices, status)

def resolve_ip(ip):
    name, alias, addresslist = socket.gethostbyaddr(ip)
    return (name)

def resolve_hostname(hostname):
    ais = socket.getaddrinfo(hostname,0,0,0,0)
    return (str(ais[1][4][0]))

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

def insert_query_builder(ip, hostname):
    try:
        if check_if_exists_with_ip(ip) != False:
            sql = "INSERT INTO devices (`ip`, `hostname`, `first_seen`, `last_status`) VALUES ({}, {}, CURRENT_TIMESTAMP(), {});".format(ip, hostname, get_single_status_nmap(ip))
        else:
            sql = "UPDATE devices SET (`ip`, `hostname`, `updated_at`, `last_status`) VALUES ({}, {}, CURRENT_TIMESTAMP(), {}) WHERE ip='{}'".format(ip, hostname, get_single_status_nmap(ip), ip)
        print (sql)
        cursor.execute(sql)
        db.commit()
    except Exception as err:
        return err

def db_handler():
    threading.Timer(30.0, db_handler).start()
    ip = edgeos_vbash_runner("vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $1}'")
    hostname = edgeos_vbash_runner("vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $6}'")

    dangit = [list(a) for a in zip(ip, hostname)]
    for item in dangit:
        insert_query_builder(item[0], item[1])

@app.route("/", methods=['GET', 'POST'])
def show_devices():
    routerIp = getters.get_envvars_routerip()
    routerUser = getters.get_envvars_routerUser()
    routerPass = getters.get_envvars_routerPass()
    getDevices = edgeos_get_dhcp_leases(routerIp, routerUser, routerPass, output={}, hostname="vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $6}'", port=22)

    #db_handler() # runs every 5 minutes
    prettifyDevices = prettify_json(getDevices)
    return render_template("index.html", devices=prettifyDevices, lastUpdate=now())

@app.route("/get/devices", methods=['GET'])
def get_devices():
    routerIp = getters.get_envvars_routerip()
    routerUser = getters.get_envvars_routerUser()
    routerPass = getters.get_envvars_routerPass()
    getDevices = edgeos_get_dhcp_leases(routerIp, routerUser, routerPass, output={}, hostname="vbash -c -i 'show dhcp leases' | awk -F' ' 'NR>2 {print $6}'", port=22)
    return getDevices

'''
 Calls:
 /get/status?ip=<ip.of.device>
 /get/status?hostname=<hostname>

 Returns:
 UP || DOWN
'''
@app.route("/get/status", methods=['GET'])
def get_status():
    ip = request.args.get('ip', '', type=str)
    deviceName = request.args.get('hostname', '', type=str)

    if (deviceName != None):
        getStatus = (get_ip_status(resolve_hostname(deviceName)))
        results = {}
        results[resolve_ip(getStatus[0][0])] = getStatus[0][1].upper()
        return results

    if (ip != None):
        getStatus = (get_ip_status(ip))
        results = {}
        results[getStatus[0][0]] = getStatus[0][1].upper()
        return results

    if (ip == None and deviceName == None):
        return "Error: Unable to get status as there is no IP or hostname specified"

    # elif (deviceName == None):
    #     getStatus = (get_ip_status(ip))
    #     results = {}
    #     results[getStatus[0][0]] = getStatus[0][1].upper()
    #     return results
    # elif (ip == None):
    #     getStatus = (get_ip_status(resolve_hostname(deviceName)))
    #     results = {}
    #     results[resolve_ip(getStatus[0][0])] = getStatus[0][1].upper()
    #     return results
    # else:
    #     return "Error: Unable to function"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')
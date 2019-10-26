# CHANGELOG

## 0.0.3
- modified API endpoints:
- getting devices is now http://localhost/get/devices
- getting status of a particular device, return response is based on api endpoint you use, so either do http://localhost/get/status?ip=127.0.0.1 for a response of {'IP': 'STATUS'} or http://localhost/get/status?hostname=localhost for {'HOSTNAME': 'STATUS'}. can use either ip or hostname for values in the get, but it will return with what endpoint you choose to use.
- added requirements file

## 0.0.2
- refreshes every 60 seconds
- grabs status of each devices and displays UP/DOWN
- get credentials via environment variables

## 0.0.1
- initial upload
- copy/paste code form LANDiscover to log into my ubiquiti router
- use flask to display JSON
- update page every 5 seconds

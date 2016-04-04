#!/bin/bash
sudo python /home/pi/vin/vingateway_21feb16/manage.py ngrokstart &
sudo python /home/pi/vin/vingateway_21feb16/manage.py runserver &
exit 0

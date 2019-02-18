# nagios_silverpeak_api

## Nagios Silver Peak API Plugin: 

  `nagios_silverpeak_api.py` is written in python 3 and is used to monitor the Silver peak WAN SD network devices resources through REST API.

Usage: silverpeak_api.py [options]
----------------------------------

Options:



  --version             show program's version number and exit
  
  
  -h, --help            show this help message and exit
  
  
  -H HOST, --host=HOST  Name/IP Address of the silverpeak device
  
  
  -O OPTION, --option=OPTION
  
                        memory / swap / alarms / tunnels / nexthops / vrrp / diskinfo
                        
                        
  -W WARN, --warning=WARN
  
                        Warning threshold
                        
                        
  -C CRIT, --critical=CRIT
  
                        Critical threshold

Examples
--------

  python nagios_silverpeak_api.py -H hostname -O diskusage -W 80 -C 90  
  python nagios_silverpeak_api.py -H hostname -O alarms  
  python nagios_silverpeak_api.py -H hostname -O memory -W 80 -C 90

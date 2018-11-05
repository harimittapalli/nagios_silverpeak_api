#!/usr/bin/python -W ignore

import pandas as pd
import requests
import os,sys,re
from optparse import OptionParser


################################################################################
# Option Parser
################################################################################
parser = OptionParser(version = "0.2.1")


parser.add_option('-H','--host',
    dest='hostname',
    default='',
    metavar='HOST',
    help=('Name/IP Address of the silverpeak device'))

parser.add_option('-O','--option',
    dest='option',
    default='',
    metavar='OPTION',
    help=('Memroy Usage / Swap Usage / Alarms / tunnels '))

parser.add_option('-W','--warning',
    dest='warning',
    default='',
    metavar='WARN',
    help=('Warning threshold '))
parser.add_option('-C','--critical',
    dest='critical',
    default='',
    metavar='CRIT',
    help=('Critical threshold threshold '))

(opts, arg) = parser.parse_args()
ipaddr=opts.hostname
option=opts.option
warn=opts.warning
crit=opts.critical

def memory_usage():

        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)


        mem_url="https://{}/rest/json/memory".format(ipaddr)
        mem=s.request("GET",mem_url,verify=False)

        if mem.status_code != 200:
                print mem.content
                sys.exit(3)
                return ''
        memory_data=mem.json()
        _tot_mem=float(memory_data['total'] / 1024)
        _free_mem=float(memory_data['free'] / 1024)
        _used_mem=float(memory_data['used'] / 1024)
        tot_swap=float(memory_data['swapTotal'] / 1024)
        free_swap=float(memory_data['swapFree'] / 1024)
        used_swap=float(memory_data['swapUsed'] / 1024)
        tot_mem = _tot_mem + tot_swap
        free_mem = _free_mem + free_swap
        used_mem = _used_mem + used_swap
        pm_used=( used_mem / tot_mem )*100
#print(pm_used)
        if pm_used > int(crit):
            print('Critical: Memory Usage is {0:.2f} %, {3:.2f}MB is used of total {1:.2f}MB | total={1:.2f},free={2:.2f}'.format(pm_used,tot_mem,free_mem,used_mem))
            status=2
        elif pm_used > int(warn) :
            print('Warning: Memory Usage is {0:.2f} % , {3:.2f}MB is used of total {1:.2f}MB | total={1:.2f},free={2:.2f}'.format(pm_used,tot_mem,free_mem,used_mem))
            status=1
        else:
            print('OK: Memory Usage is {0:.2f} % , {3:.2f}MB is used of total {1:.2f}MB | total={1:.2f},free={2:.2f}'.format(pm_used,tot_mem,free_mem,used_mem))
            status=0
        logout=s.request("GET",logout_url,verify=False)
        s.close()
        sys.exit(status)
def swap_usage():
        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)


        mem_url="https://{}/rest/json/memory".format(ipaddr)
        mem=s.request("GET",mem_url,verify=False)

        mem.json()

        memory_data=mem.json()
        tot_mem=float(memory_data['total'] / 1024)
        free_mem=float(memory_data['free'] / 1024)
        used_mem=float(memory_data['used'] / 1024)
        tot_swap=float(memory_data['swapTotal'] / 1024)
        free_swap=float(memory_data['swapFree'] / 1024)
        used_swap=float(memory_data['swapUsed'] / 1024)

        pm_used=( used_swap / tot_swap )*100
#print(pm_used)
        if pm_used > int(crit):
            print('Critical: Memory Usage is {0:.2f} %, {3:.2f}MB is used of total {1:.2f}MB | total={1:.2f},free={2:.2f}'.format(pm_used,tot_swap,free_swap,used_swap))
            status=2
        elif pm_used > int(warn) :
            print('Warning: Memory Usage is {0:.2f} % , {3:.2f}MB is used of total {1:.2f}MB | total={1:.2f},free={2:.2f}'.format(pm_used,tot_swap,free_swap,used_swap))
            status=1
        else:
            print('OK: Memory Usage is {0:.2f} % , {3:.2f}MB is used of total {1:.2f}MB | total={1:.2f},free={2:.2f}'.format(pm_used,tot_swap,free_swap,used_swap))
            status=0
        logout=s.request("GET",logout_url,verify=False)
        s.close()
        sys.exit(status)

def tunnel_status():
        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)


        tunnel_url="https://{}/rest/json/tunnelsConfigAndState".format(ipaddr)
        tunnel=s.request("GET",tunnel_url,verify=False)
        if tunnel.status_code != 200:
                print tunnel.content
                sys.exit(3)
                return ''
        t_output=tunnel.json()
        _df=pd.DataFrame(t_output)
        df=_df.T
        df['Tunnels'] = df.index
        crit_tunnels=df.loc[(df['status'] != 'Up - Active') & (~df.Tunnels.isin(['default','pass-through','pass-through-unshaped']))]

        if len(crit_tunnels) > 0:
            print('Critical: Below Tunnels status is not Up - Active , kindly check. {}'.format(crit_tunnels['Tunnels']))
            status=2
        else:
            print('OK: All Tunnels are UP and Active. \n{}'.format(df['status']))
            status=0
        s.close()
        sys.exit(status)

def alarms():
        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)

        url="https://{}/rest/json/alarm".format(ipaddr)
        alarm=s.request("GET",url,verify=False)

        a_data=alarm.json()
        alarms=[]
        status_info=""
        if len(a_data['outstanding']) > 0:
            ind=1
            status=2
            status_info+="CRITCAL: "
            try:
             for al in a_data['outstanding']:
                alarms.append(al)
                ind+=1
                if al['acknowledged'] == True:
                    continue
                status_info+=al['description']+"\n"
            except:
             status=1
             status_info=a_data
        else:
            status=0
            status_info+="OK: No Alarms present on the device"
        print(status_info)
        s.close()
        sys.exit(status)
def nexthops():
        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)

        url="https://{}/rest/json/nexthops".format(ipaddr)
        nexthops=s.request("GET",url,verify=False)
        if nexthops.status_code != 200:
                print nexthops.content
                sys.exit(3)
                return ''
        err_info=''
        ok_info=''
        for hop in nexthops.json():
            if hop['nhop_state'] == 'reachable':
                ok_info+=hop['nhop_ifname']+' : '+hop['nhop_state']+' , '
                #print(hop['nhop_ifname'],' : ',hop['nhop_state'])
            else:
                err_info+=hop['nhop_ifname']+' : '+hop['nhop_state']+' , '
        if err_info:
            print 'CRITICAL: ',err_info
            status=2
        else:
            print 'OK: ',ok_info
            status=0

        s.close()
        sys.exit(status)

def vrrp():
        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)

        url="https://{}/rest/json/vrrp".format(ipaddr)
        vrrp=s.request("GET",url,verify=False)
        if vrrp.status_code != 200:
                print vrrp.content
                sys.exit(3)
                return ''
        if vrrp.status_code == 200 :
          if vrrp.json():
                uptime=vrrp.json()[0]['uptime']
                interface=vrrp.json()[0]['interface']
                print interface,'is UP for',uptime
          else:
                print 'No VRRP Information for the host'
        else:
                print 'No VRRP Information for the host'
        status=0
        s.close()
        sys.exit(status)
def diskinfo():
        login_url = "https://{}/rest/json/login".format(ipaddr)
        logout_url=  "https://{}/rest/json/logout".format(ipaddr)

        querystring = {"user":"monitor","password":"monitor"}

        s = requests.Session()
        response = s.request("GET",login_url, params=querystring,verify=False)

        url="https://{}/rest/json/diskusage".format(ipaddr)
        diskinfo=s.request("GET",url,verify=False)
        if diskinfo.status_code != 200:
                print diskinfo.content
                sys.exit(3)
                return ''
        warn_info='WARNING: '
        crit_info='CRITCAL: '
        ok_info='OK: '
        disk_data=diskinfo.json()
        for key in disk_data.keys():
            #print(disk_data[key])
            u_percent=disk_data[key]['usedpercent']
            f_system=disk_data[key]['filesystem']
            if u_percent > crit:
                crit_info+="{} is {}% used".format(f_system,u_percent)+";"

            elif u_percent > warn:
                warn_info+="{} is {}% used".format(f_system,u_percent)+";"

            else:
                ok_info+="{} is {}% used".format(f_system,u_percent)+";"
        if crit_info != 'CRITCAL: ' and warn_info !='WARNING: ':
            print(crit_info,"\n",warn_info,"\n",ok_info)
            status=2
        elif crit_info != 'CRITCAL: ':
            print(crit_info,"\n",ok_info)
            status=2

        elif warn_info !='WARNING: ':
            print(warn_info,"\n",ok_info)
            status=1
        else:
            print(ok_info)
            status=0
        s.close()
        sys.exit(status)

if option == "memory":
        memory_usage()
elif option == "swap":
        swap_usage()
elif option == "tunnels":
        tunnel_status()
elif option == "alarms":
        alarms()
elif option == "nexthops":
        nexthops()
elif option == "vrrp":
        vrrp()
elif option == "diskinfo":
        diskinfo()

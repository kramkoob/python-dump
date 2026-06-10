# checker.py
# Searches the entire address range for instruments (except oscilloscopes) and verifies their hostname.
# By Thomas Dodds
# 6/9/2026

import pyvisa
rm = pyvisa.ResourceManager()

for i in range(130,202):
    ip = '10.20.18.%d' % i
    try:
        with rm.open_resource('TCPIP0::%s::inst0::INSTR' % ip) as inst:
            instmodel = inst.query('*IDN?').split(',')[1]
            if instmodel == "EDUX1052G":
                continue
            hostname = inst.query('SYSTem:COMMunicate:LAN:HOSTname?').strip().split("\"")[1]
            station = (i - 130) // 4 + 1
            wanted_hostname = '%s-%d' % (instmodel, station)
            print(wanted_hostname, end=" ")
            if(hostname != wanted_hostname):
                print("%s is actually %s." % (ip, hostname), end=' ')
                if input("Update? (y/n) ") == 'y':
                    inst.write('SYSTem:COMMunicate:LAN:HOSTname "%s"' % wanted_hostname)
                    inst.write('SYSTem:COMMunicate:LAN:UPDate')
            else:
                print("OK")
    except pyvisa.VisaIOError:
        print('No instrument at IP %s' % ip)
        pass
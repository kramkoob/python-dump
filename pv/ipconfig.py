# instrument IP updater
# give station ID and list current instrument IPs at that station, and automatically:
# * determines instrument model
# * updates instrument IP according to new scheme
# * sets hostname
# does not work for oscilloscopes

# By Thomas Dodds
# 6/9/2026

import pyvisa
rm=pyvisa.ResourceManager()

insttable = {
    'EDUX1052G':4, #scope
    'EDU33212A':3, #wavegen
    'EDU34450A':2, #meter
    'EDU36311A':1  #power supply
}

print("You will be asked for a station ID and then each instrument's current IP.")
print("Return to station select by leaving IP blank and pressing enter.")

dns = input("Enter DNS IP: ")

while True:
    station = int(input("Enter station ID: "))
    while True:
    #for i in range(130,202):
        ip = input("Station %d: Enter instrument IP: " % station)
        #station = (i - 130) // 4 + 1
        #ip = "10.20.18.%d" % i
        if ip == "":
            break
        try:
            with rm.open_resource("TCPIP::%s::inst0::INSTR" % ip) as inst:
                idn = inst.query('*IDN?')
                model = idn.split(',')[1]
                offset = insttable[model]
                hostname = "%s-%s" % (model, station)
                ip = "10.20.18." + str((128+(int(station)-1)*4+offset+1))
                if("EDUX1052G" in idn):
                    print("Oscilloscopes do not support remote IP configuration.")
                    print("Use the front panel to configure:")
                    print("\tDHCP: Off")
                    print("\tIP: %s." % ip)
                    print("\tGateway: %s." % "10.20.18.129")
                    print("\tDNS: %s." % dns)
                    print("\tSubnet Mask: %s." % "255.255.255.128")
                    print("\tHostname: %s." % hostname)
                else:
                    print("Configuring station %s %s to new IP %s" % (station, model, ip))
                    inst.write('SYST:COMMunicate:LAN:DHCP 0')
                    inst.write('SYST:COMMunicate:LAN:IPADdress "%s"' % ip)
                    inst.write('SYST:COMMunicate:LAN:GATEway "%s"' % "10.20.18.129")
                    inst.write('SYST:COMMunicate:LAN:DNS "%s"' % dns)
                    inst.write('SYST:COMMunicate:LAN:SMASk "%s"' % "255.255.255.128")
                    inst.write('SYST:COMMunicate:LAN:HOSTname "%s"' % hostname)
                    inst.write('SYST:COMMunicate:LAN:UPDate')
        except Exception as e:
            #pass
            print("Error configuring station %s at IP %s:\n%s" % (station, ip, e))


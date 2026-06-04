# pyvisa-test2
# 5/25/26
# By Thomas Dodds

# Same as test1 (measuring a filter) but only uses power supply and scope

# Scope wavegen ch1 to filter input
# Scope ch1 to filter input
# Scope ch2 to filter output
# Power ch2/3 as bipolar for opamp

#%% Configure addresses and import libraries
_SCOPE = "TCPIP0::10.20.18.151::hislip0::INSTR"
_POWER = "TCPIP::10.20.18.141::inst0::INSTR"

import pyvisa
import matplotlib.pyplot as plt
import numpy as np
#%% Connect and reset instruments
print("Connecting:")
rm = pyvisa.ResourceManager()
scope = rm.open_resource(_SCOPE)
print(scope.query("*IDN?"), end='')
scope.write("*RST")

power = rm.open_resource(_POWER)
print(power.query("*IDN?"), end='')
power.write("*RST")
# %% Set power output to +/-15V, enable tracking, and turn on
power.write('source:voltage:level 15, (@2)')
power.write('output:track:state 1')
power.write('output:state 1, (@2,3)')
# %%Set scope and scope wavegen
scope.write(':wgen:frequency 1000')
scope.write(':wgen:function sinusoid')
scope.write(':wgen:output:load onemeg')
scope.write(':wgen:voltage 1')
scope.write(':wgen:voltage:offset 0')
scope.write(':wgen:output 1')

scope.write(':acquire:type hresolution')
scope.write(':timebase:range 0.001')
scope.write(':timebase:position 0')

scope.write(':channel1:probe 1') #attenuation
scope.write(':channel1:range 1 V')
scope.write(':channel1:offset 0')
scope.write(':channel1:display 1')
scope.write(':channel1:coupling DC')

scope.write(':channel2:probe 1')
scope.write(':channel2:range 1 V')
scope.write(':channel2:offset 0')
scope.write(':channel2:display 1')
scope.write(':channel2:coupling DC')

scope.write(':trigger:edge:source wgen')
scope.write(':trigger:sweep normal')
scope.write(':trigger:edge:level 0,channel1')
scope.write(':single')
# %% Perform test
vinlist = []
voutlist = []
dblist = []
vscale = 1
flist = np.logspace(0,5,50)
adj = False
scope.write(':channel2:range 1 V')
scope.write(':channel2:offset 0')
# Iterate:
for f in flist:
    # Set Frequency
    scope.write(':wgen:frequency %d' % f)
    scope.write(':single')
    # Scale scope
    if not adj and f >= 1000:
        # switch to AC coupling at high frequency - no impact to measurements
        adj = True
        scope.write(':channel1:coupling AC')
        scope.write(':channel2:coupling AC')
    hscale = 1.0 / f
    scope.write(':timebase:range %f' % hscale)
    # Measure pk-pk
    while True:
        try:
            # at low frequencies this may take a while
            vin = scope.query_ascii_values(':measure:vpp? channel1')[0]
            break
        except pyvisa.VisaIOError:
            pass
    vout = scope.query_ascii_values(':measure:vpp? channel2')[0]
    # Scale output channel if necessary
    if vout < vscale/2:
        vscale = vscale/2
        scope.write(':channel2:range %f V' % vscale)
        vout = scope.query_ascii_values(':measure:vpp? channel2')[0]
    # Calculate dB gain
    db = 20 * np.log10(vout/vin)
    # Record values
    vinlist.append(vin)
    voutlist.append(vout)
    dblist.append(db)
    print('Freq: %d\t In: %f\t Out: %f\t dB: %f\t hscale: %f\t vscale: %f' % (f, vin, vout, db, hscale, vscale))
# %% Disable instruments after test
scope.write("*RST")
power.write("*RST")
# %% Plot values
plt.plot(flist, voutlist)
plt.title('Vout vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Voltage (V)')
plt.yscale('log') # Set y-axis to logarithmic scale
plt.xscale('log') # Set y-axis to logarithmic scale
plt.show()
# %%
plt.plot(flist, dblist)
plt.title('Gain vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.xscale('log') # Set y-axis to logarithmic scale
plt.show()
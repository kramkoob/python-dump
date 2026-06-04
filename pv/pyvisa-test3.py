# pyvisa-test3
# 5/25/26
# By Thomas Dodds

# Same as test1 (measuring a filter) but only uses scope (no opamp)

# Scope wavegen ch1 to filter input
# Scope ch1 to filter input
# Scope ch2 to filter output

#%% Configure addresses and import libraries
_SCOPE = "TCPIP0::10.20.18.151::hislip0::INSTR"

import pyvisa
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

print("Connecting:", end=' ')
rm = pyvisa.ResourceManager()
scope = rm.open_resource(_SCOPE)
print(scope.query("*IDN?"), end='')
scope.write("*RST")
# %%Set scope and scope wavegen, perform test
scope.write(':wgen:frequency 1000')
scope.write(':wgen:function sinusoid')
#scope.write(':wgen:output:load onemeg')
scope.write(':wgen:output:load fifty')
scope.write(':wgen:voltage 10')
scope.write(':wgen:voltage:offset 0')
scope.write(':wgen:output 1')

scope.write(':acquire:type hresolution')

scope.write(':timebase:range 0.001')
scope.write(':timebase:position 0')

scope.write(':channel1:probe 10') #attenuation
scope.write(':channel1:range 10 V')
scope.write(':channel1:offset 0')
scope.write(':channel1:display 1')
scope.write(':channel1:coupling DC')

scope.write(':channel2:probe 10')
scope.write(':channel2:range 10 V')
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
vscale = 10
flist = np.logspace(-1,np.log10(20000000),30)
adj = False
scope.write(':channel2:range 10 V')
scope.write(':channel2:offset 0')
# Iterate:
for f in tqdm(flist, desc='Measuring', unit="meas"):
    # Set Frequency
    scope.write(':wgen:frequency %f' % f)
    scope.write(':single')
    # Scale scope
    if not adj and f >= 1000:
        # switch to AC coupling at high frequency - no impact to measurements
        adj = True
        scope.write(':channel1:coupling AC')
        scope.write(':channel2:coupling AC')
    if f < 1000000:
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
    # Rescale output channel if necessary, and remeasure
    if vout < vscale/2:
        vscale = vscale/2
        #scope.write(':channel2:range %f V' % vscale)
        scope.write(':single')
        while True:
            try:
                vin = scope.query_ascii_values(':measure:vpp? channel1')[0]
                break
            except pyvisa.VisaIOError:
                pass
        vout = scope.query_ascii_values(':measure:vpp? channel2')[0]
    # Calculate dB gain
    db = 20 * np.log10(vout/vin)
    # Record values
    vinlist.append(vin)
    voutlist.append(vout)
    dblist.append(db)
    #print('Freq: %f\t In: %f\t Out: %f\t dB: %f\t vscale: %f' % (f, vin, vout, db, vscale))
scope.write("*RST")
# %% Plot vout and vin values
plt.plot(flist, vinlist, label="Vin")
plt.plot(flist, voutlist, label="Vout")
plt.title('Vout vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Voltage (V)')
#plt.yscale('log') # Set y-axis to logarithmic scale
plt.xscale('log') # Set x-axis to logarithmic scale
plt.grid()
plt.legend()
plt.show()
# %% Plot gain
plt.plot(flist, dblist)
plt.title('Gain vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.xscale('log') # Set x-axis to logarithmic scale
plt.grid()
plt.show()

# %%

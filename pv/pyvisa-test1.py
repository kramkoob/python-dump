# pyvisa-test1
# 5/18/26
# By Thomas Dodds

# Auto-configure all four instruments to do filter measurements.

# Wavegen ch1 to filter input
# Scope ch1 to filter input
# Scope ch2 to filter output
# Power ch2/3 as bipolar for opamp
# Relay to swtich between filter input and output
# Relay coil to ch1 of power supply (may need transistor from ch2)
# Relay NC to filter output
# Relay NO to filter input
# Meter to common contact of relay

#%% Configure addresses and import libraries
_SCOPE = "TCPIP0::10.20.18.151::hislip0::INSTR"
_METER = "TCPIP::10.20.18.142::inst0::INSTR"
_WAVEGEN = "TCPIP::10.20.18.191::inst0::INSTR"
_POWER = "TCPIP::10.20.18.141::inst0::INSTR"

import pyvisa
import matplotlib.pyplot as plt
import numpy as np
#%% Connect and reset instruments
print("Connecting:")
rm = pyvisa.ResourceManager()
scope = rm.open_resource(_SCOPE, open_timeout=5000)
print(scope.query("*IDN?"), end='')
scope.write("*RST")

meter = rm.open_resource(_METER, open_timeout=5000)
print(meter.query("*IDN?"), end='')
meter.write("*RST")

wavegen = rm.open_resource(_WAVEGEN, open_timeout=5000)
print(wavegen.query("*IDN?"), end='')
wavegen.write("*RST")

power = rm.open_resource(_POWER, open_timeout=5000)
print(power.query("*IDN?"), end='')
power.write("*RST")
# %% Set power output to +/-15V, enable tracking, and turn on
power.write('source:voltage:level 15, (@2)')
power.write('output:track:state 1')
power.write('output:state 1, (@2,3)')
# Set ch1 to 6v 0.1a
power.write('source:voltage:level 6, (@1)')
power.write('source:current:level 0.1, (@1)')
# %%Set wavegen output to inf output impedance, 1Vp-p 50Hz sine, and turn on
wavegen.write('output1:load inf')
wavegen.write('source1:function sin')
wavegen.write('source1:frequency 50')
wavegen.write('source1:voltage 1Vpp')
wavegen.write('source1:voltage:offset 0')
wavegen.write('output1:state 1')
# %%Scale scope
scope.write(':acquire:type hresolution')
#scope.write(':autoscale')
scale = 1.0 / 50
scope.write(':timebase:range %f' % scale)
scope.write(':timebase:position 0')
# Range sets the entire screen, instead of /div (scale)
scope.write(':channel1:probe 1') #attenuation
scope.write(':channel1:range 1 V')
scope.write(':channel1:offset 0')
scope.write(':channel1:display 1')
scope.write(':channel2:probe 1')
scope.write(':channel2:range 1 V')
scope.write(':channel2:offset 0')
scope.write(':channel2:display 1')
scope.write(':trigger:edge:level 0,channel1')
# %% Set meter for scaling and acquire reference
power.write('output:state 1, (@1)')
meter.write('configure:primary:voltage:ac 1 V,slow')
meter.write('trigger:source immediate')
meter.write('initiate')
meter.write('calculate:function db')
# When db scale is first selected and enabled, reference value is recorded
meter.write('calculate:state 1')
# Wait for first measurement to stabilize
while True:
    try:
        # Throws exception if it takes too long.
        # Meter may warn about this, but it's alright
        meter.query_ascii_values('read?')[0]
        break
    except pyvisa.VisaIOError:
        continue
power.write('output:state 0, (@1)')
# %% Perform test
vinlist = []
voutlist = []
dblist = []
scopedblist = []
vscale = 1
flist = np.logspace(1,5,20)
adj = False
# Iterate:
for f in flist:
    # Set Frequency
    wavegen.write('source1:frequency %d' % f)
    # Scale scope
    hscale = 1.0 / f
    scope.write(':timebase:range %f' % hscale)
    scope.write(':channel1:offset 0')
    scope.write(':channel2:offset 0')
    # Measure pk-pk
    vin = scope.query_ascii_values(':measure:vpp? channel1')[0]
    vout = scope.query_ascii_values(':measure:vpp? channel2')[0]
    # Scale output channel if necessary
    if vout < vscale/2:
        vscale = vscale/2
        scope.write(':channel2:range %f V' % vscale)
        vout = scope.query_ascii_values(':measure:vpp? channel2')[0]
    # Scale multimeter if necessary
    if vout <= .1 and not adj:
        adj = True
        meter.write('sense:primary:voltage:ac:range 100 mV')
    # Measure dB from meter
    while True:
        try:
            # While loop waits for valid response/measurement
            db = meter.query_ascii_values('read?')[0]
            break
        except pyvisa.VisaIOError:
            continue
    # Record values
    vinlist.append(vin)
    voutlist.append(vout)
    dblist.append(db)
    scopedblist.append(20 * np.log10(np.array(vout)/np.array(vin)))
    print('Freq: %d\t In: %f\t Out: %f\t dB: %f\t hscale: %f\t vscale: %f' % (f, vin, vout, db, hscale, vscale))
# %% Disable instruments after test
scope.write("*RST")
meter.write("*RST")
power.write("*RST")
wavegen.write("*RST")
# %% Plot voltages
plt.plot(flist, voutlist, label="Input")
plt.plot(flist, vinlist, label="Output")
plt.legend()
plt.title('Voltage vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Peak-Peak Voltage (V)')
#plt.yscale('log') # Set y-axis to logarithmic scale
plt.xscale('log') # Set y-axis to logarithmic scale
plt.grid()
plt.show()
# %% Plot gain
plt.plot(flist, dblist, label='Meter')
plt.plot(flist, scopedblist, label='Scope')
plt.legend()
plt.title('Gain vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Gain (dB)')
plt.xscale('log') # Set y-axis to logarithmic scale
plt.grid()
plt.show()
# %%

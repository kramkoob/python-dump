# resetter.py
# goes through all instruments in the IP range and performs resets, self tests, and clock settings
# wavegen: also sets impedance to high-Z

# 5/26/26
# By Thomas Dodds

# %% Initialization - ideally only run once
import pyvisa
from tqdm import tqdm
from datetime import datetime
from itertools import chain

rm = pyvisa.ResourceManager()
insts = {
    'EDUX1052G':[],
    'EDU33212A':[],
    'EDU34450A':[],
    'EDU36311A':[]
}
"""
_SCOPE = "10.20.18.151"
_METER = "10.20.18.142"
_WAVEGEN = "10.20.18.191"
_POWER = "10.20.18.141"
insts = {
    'EDUX1052G':[_SCOPE],
    'EDU33212A':[_WAVEGEN],
    'EDU34450A':[_METER],
    'EDU36311A':[_POWER]
}
"""
# %% Choose test
if len(insts['EDUX1052G']) == 0:
    test = ['10.20.18.%d' % i for i in range(130,202)]
else:
    test = sorted(set(chain.from_iterable(insts.values())))
# %% Run test
for ip in tqdm(test):
    try:
        with rm.open_resource('TCPIP0::%s::inst0::INSTR' % ip) as inst:
            instid = inst.query('*IDN?')
            instmodel = instid.split(',')[1]
            if instmodel not in ('EDU34450A', 'EDU33212A', 'EDU36311A', 'EDUX1052G'):
                print('Unknown instrument at %s:\n%s' % (ip, instid))
                continue
            inst.write('*RST') # Reset
            inst.write('*CLS') # Clear error queue etc.
            # Date and time are common to every instrument
            t = datetime.now()
            inst.write('SYST:DATE %d,%d,%d' % (t.year,t.month,t.day))
            inst.write('SYST:TIME %d,%d,%d' % (t.hour,t.minute,t.second))
            # Wavegen: Set load to high-z. This is saved w/ power-down state
            if instmodel == 'EDU33212A':
                inst.write('OUTP1:LOAD INF')
                inst.write('OUTP2:LOAD INF')
            
            # Visual indicators
            if instmodel == 'EDUX1052G':
                # Stop scope
                inst.write('DISP 1')
            elif instmodel == 'EDU34450A':
                pass
                # 
            else: #scope
                inst.write('STOP')
            # Instrument self-test
            inst.write('*TST?')
            # Add to test list if it isn't there
            print('Reset instrument %s at IP %s' % (instmodel, ip))
            if ip not in insts[instmodel]:
                insts[instmodel].append(ip)
    except pyvisa.VisaIOError:
        pass
# %%

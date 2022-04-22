#This script is meant to serve as a basic communication script with arduino, ultimately serving as a serial monitor
#Makes use of the PyVISA library
############### PyVISA test 1 ###############

import pyvisa
#import time


rm = pyvisa.ResourceManager()
rm.list_resources()
('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::14::INSTR', 'ASRL20::INSTR')
my_instrument = rm.open_resource('ASRL20::INSTR')
print(my_instrument.query('*IDN?'))
while True:
    print(my_instrument.read_bytes(50))
    #time.sleep(1)
"""
Service Explorer
----------------

An example showing how to access and print out the services, characteristics and
descriptors of a connected GATT server.

Created on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>

"""

import sys
import platform
import asyncio
import logging
import time
from bleak import BleakClient

logger = logging.getLogger(__name__)

ADDRESS = "bc:6a:29:ab:4d:08" # TI sensor

TI_BASE_UUID = "F000{0:X}-0451-4000-B000-000000000000"
TI_IR_DATA_UUID = TI_BASE_UUID.format(0xAA01)
#TI_IR_NOTIFY_UUID = TI_BASE_UUID.format(0xAA01)
TI_IR_CONFIG_UUID = TI_BASE_UUID.format(0xAA02)
TI_IR_PERIOD_UUID = TI_BASE_UUID.format(0xAA03)

tosigned = lambda n: float(n-0x10000) if n>0x7fff else float(n)
tosignedbyte = lambda n: float(n-0x100) if n>0x7f else float(n)

def calcTmpTarget(objT, ambT):
  objT = tosigned(objT)
  ambT = tosigned(ambT)

  m_tmpAmb = ambT/128.0
  Vobj2 = objT * 0.00000015625
  Tdie2 = m_tmpAmb + 273.15
  S0 = 6.4E-14            # Calibration factor
  a1 = 1.75E-3
  a2 = -1.678E-5
  b0 = -2.94E-5
  b1 = -5.7E-7
  b2 = 4.63E-9
  c2 = 13.4
  Tref = 298.15
  S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
  Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
  fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
  tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
  tObj = (tObj - 273.15)
  return tObj

def hexTemp2C(raw_temperature):
    raw_ambient_temp = int.from_bytes(raw_temperature[2:4], "little")
    raw_IR_temp = int.from_bytes(raw_temperature[0:2], "little")
    IR_temp_int = raw_IR_temp >> 2 & 0x3FFF
    ambient_temp_int = raw_ambient_temp >> 2 & 0x3FFF # Shift right, based on from TI
    ambient_temp_celsius = float(ambient_temp_int) * 0.03125 # Convert to Celsius based on info from TI
    IR_temp_celsius = float(IR_temp_int)*0.03125
    ambient_temp_fahrenheit = (ambient_temp_celsius * 1.8) + 32 # Convert to Fahrenheit
    return (IR_temp_celsius, ambient_temp_celsius)

async def main(address):
    async with BleakClient(address) as client:
        logger.info(f"Connected: {client.is_connected}")
        write_value = bytearray([0x01])
        value = await client.read_gatt_char(TI_IR_CONFIG_UUID)
        print("I/O Data Pre-Write Value: {0}".format(value))
        await client.write_gatt_char(TI_IR_CONFIG_UUID, write_value)
        value = await client.read_gatt_char(TI_IR_CONFIG_UUID)
        print("I/O Data Post-Write Value: {0}".format(value))
        while True:
            value = await client.read_gatt_char(TI_IR_DATA_UUID)
            print(hexTemp2C(value))
            time.sleep(2) 

if __name__ == "__main__":
    logging.basicConfig(filename="./log.txt", level=logging.INFO)
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))

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

async def main(address):
    async with BleakClient(address) as client:
        logger.info(f"Connected: {client.is_connected}")

        write_value = bytearray([0x01])
        value = await client.read_gatt_char(TI_IR_CONFIG_UUID)
        print("I/O Data Pre-Write Value: {0}".format(value))
        #await client.write_gatt_char(TI_IR_CONFIG_UUID, write_value)
        value = await client.read_gatt_char(TI_IR_CONFIG_UUID)
        print("I/O Data Post-Write Value: {0}".format(value))
        while True:
            value = await client.read_gatt_char(TI_IR_DATA_UUID)
            print(value)
            time.sleep(2) 

if __name__ == "__main__":
    logging.basicConfig(filename="./log.txt", level=logging.INFO)
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))

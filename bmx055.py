'''
bmx055 is a micropython module for the Bosch BMX055 sensor.
It measures acceleration, turn rate and the magnetic field in three axis.

The MIT License (MIT)

Copyright (c) 2016 Sebastian Plamauer oeplse@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import machine

# from stackoverflow J.F. Sebastian
def _twos_comp(val, bits=8):
    """compute the 2's complement of int val with bits"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


class BMX055():

    def __init__(self, i2c):

        if type (i2c) == machine.I2C:
            self.i2c = i2c
        else:
            raise TypeError('passed argument is not an I2C object')
        self.accel = BMA2X2(self.i2c)
        self.gyro = BMG160(self.i2c)
#        self.mag = BMM050(self.i2c)


class BMA2X2():
    '''accelerometer'''

    def __init__(self, i2c):

        self.i2c = i2c
        self.acc_addr = 0x18
        try:
            self.chip_id = i2c.readfrom_mem(self.acc_addr, 0x00, 1)[0]
        except OSError:
            self.acc_addr = 0x19
            try:
                self.chip_id = i2c.readfrom_mem(self.acc_addr, 0x00, 1)[0]
            except OSError:
                raise OSError('no BMA2X2 connected')
        print('---', self.get_range())
        self.set_range(2)      # default range to 16g

    def _read_accel(self, addr):
        """return accel data from addr"""
        LSB, MSB = self.i2c.readfrom_mem(self.acc_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return (LSB + (MSB<<4))*self._resolution/1000

    def temperature(self):
        return self.i2c.readfrom_mem(self.acc_addr, 0x08, 1)[0]/2 + 23

    def set_range(self, accel_range):
        """set accel range to 2, 4, 8 or 16g"""
        try:
            range_byte = {2:3, 4:5, 8:8, 16:12}[accel_range]
        except KeyError:
            range_byte = 16
            print('invalid range, using 16g instead')
        print('...', hex(range_byte))
        self.i2c.writeto_mem(self.acc_addr, 0x0F, hex(range_byte))
        self._resolution = {2:0.98, 4:1.95, 8:3.91, 16:7.81}[accel_range]
        return self.get_range()

    def get_range(self):
        #return #{2:3, 4:5, 8:8, 16:12}[self.i2c.readfrom_mem(self.acc_addr, 0x0F, 1)[0]]
        return self.i2c.readfrom_mem(self.acc_addr, 0x0F, 1)

    def x(self):
        return self._read_accel(0x02)

    def y(self):
        return self._read_accel(0x04)

    def z(self):
        return self._read_accel(0x06)

    def xyz(self):
        return (self.x(), self.y(), self.z())

class BMG160():
    '''gyroscope'''

    def __init__(self, i2c):

        self.i2c = i2c
        self.gyro_addr = 0x68
        try:
            self.chip_id = i2c.readfrom_mem(self.gyro_addr, 0x00, 1)[0]
        except OSError:
            self.acc_addr = 0x69
            try:
                self.chip_id = i2c.readfrom_mem(self.gyro_addr, 0x00, 1)[0]
            except OSError:
                raise OSError('no BMG160 connected')

    def _read_gyro(self, addr):
        """return accel data from addr"""
        LSB, MSB = self.i2c.readfrom_mem(self.gyro_addr, addr, 2)
        LSB = _twos_comp(LSB)
        MSB = _twos_comp(MSB)
        return 2000*(LSB + (MSB<<8))/(2**15)

    def x(self):
        return self._read_gyro(0x02)

    def y(self):
        return self._read_gyro(0x04)

    def z(self):
        return self._read_gyro(0x06)

    def xyz(self):
        return (self.x(), self.y(), self.z())

#class BMM050():
#    '''magnetometer'''

#    def __init__(self, i2c):

#        self.i2c = i2c
#        self.chip_id = i2c.readfrom_mem(0x10, 0x40, 1)[0]

#    def _read_mag(self, addr):
#        """return accel data from addr"""
#        LSB, MSB = self.i2c.readfrom_mem(0x68, addr, 2)
#        LSB = _twos_comp(LSB)
#        MSB = _twos_comp(MSB)
#        return (LSB + (MSB<<5))/(2**15)

#    def x(self):
#        return self._read_mag(0x42)

#    def y(self):
#        return self._read_mag(0x44)

#    def z(self):
#        return self._read_mag(0x46)

#if __name__ == "__main__":
    #from bmx055 import BMX055
    #imu = BMX055()

#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>

class ADCDevice{
        
    protected:
        int _fd;
    public:
        int address;
        int cmd;
        
        ADCDevice();
        virtual ~ADCDevice(){};
        int detectI2C(int addr);
        virtual int analogRead(int chn);
        //~ADCDevice(){printf("Destructor ... \n");}
};

class ADS7830:public ADCDevice{
    public:        
        ADS7830(int addr = 0x48);  //0x4b is the default i2c address for ADS7830 Module.
        int analogRead(int chn); //ADS7830 has 8 ADC input pins, chn:0,1,2,3,4,5,6,7
};

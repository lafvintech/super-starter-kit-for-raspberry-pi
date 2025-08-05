#include "ADCDevice.hpp"

ADCDevice::ADCDevice(){
    address = 0;
    wiringPiSetup(); //Initialize wiringPi.
}

int ADCDevice::detectI2C(int addr){
    _fd = wiringPiI2CSetup (addr);   
    if (_fd < 0){		
	printf("Error address : 0x%x \n",addr);
	return 0 ;
    } 
    else{	
	if(wiringPiI2CWrite(_fd,0) < 0){
	    printf("Not found device in address 0x%x \n",addr);
	    return 0;
	}
	else{
	    printf("Found device in address 0x%x \n",addr);
	    return 1 ;
	}
    }
}

int ADCDevice::analogRead(int chn){
    printf("Implemented in subclass! \n");
    return 0;
}


ADS7830::ADS7830(int addr)
{
    address = addr;
    cmd = 0x84;
    wiringPiSetup();
    detectI2C(address);
    printf("ADS7830 setup successful! \n");
}

int ADS7830::analogRead(int chn){
    wiringPiI2CWrite(_fd, cmd|(((chn<<2 | chn>>1)&0x07)<<4));
    return wiringPiI2CRead(_fd);
}

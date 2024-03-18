#include <wiringPi.h>
#include <stdio.h>

#define slidePin		0
#define led1			3
#define led2 			2

int main(void)
{
	// When initialize wiring failed, print message to screen
	if(wiringPiSetup() == -1){
		printf("setup wiringPi failed !");
		return 1; 
	}
	
	pinMode(slidePin, INPUT);
	pinMode(led1, OUTPUT);
	pinMode(led2, OUTPUT);
	
	while(1){
		// slide switch high, led1 on
		if(digitalRead(slidePin) == 1){
			digitalWrite(led1, LOW);
			digitalWrite(led2, HIGH);
			printf("LED1 on\n");
			delay(100);
		}
		// slide switch low, led2 on
		if(digitalRead(slidePin) == 0){
			digitalWrite(led2, LOW);
			digitalWrite(led1, HIGH);
			printf(".....LED2 on\n");
			delay(100);
		}
	}

	return 0;
}



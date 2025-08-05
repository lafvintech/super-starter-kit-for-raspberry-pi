#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <getopt.h>
#include <stdlib.h>
#include <signal.h>
#include "rc522.h"

unsigned char SN[4]; 

// Function prototypes (keeping original functions)
void print_info(unsigned char *p,int cnt);
int read_card();
int card_passworld(uint8_t auth_mode,uint8_t addr,uint8_t *Src_Key,uint8_t *New_Key,uint8_t *pSnr);
uint8_t write_card_data(uint8_t *data);
uint8_t read_card_data();
void print_header();
void cleanup_and_exit();
void signal_handler(int sig);

/**
 * @brief Prints the program header with title and instructions
 */
void print_header() {
    printf("===============================================\n");
    printf("    🔖 RFID CARD WRITER 🔖\n");
    printf("===============================================\n");
    printf("This program writes text data to RFID/NFC cards.\n");
    printf("Press Ctrl+C to exit the program.\n");
    printf("===============================================\n");
}

/**
 * @brief Signal handler for graceful exit
 */
void signal_handler(int sig) {
    printf("\n\n⏹️  Program interrupted by user.\n");
    cleanup_and_exit();
}

/**
 * @brief Cleanup function
 */
void cleanup_and_exit() {
    printf("🧹 Cleaning up resources...\n");
    printf("✅ Cleanup complete. Goodbye!\n");
    exit(0);
}

int main(int argc, char **argv)
{
    uint8_t data[16]={0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22,0x23,255,255,255,255};
	uint8_t status=1;
    
    // Setup signal handler for graceful exit
    signal(SIGINT, signal_handler);
    
    // Print program header
    print_header();
    
    InitRc522();		 
	memset(data,0,16);
	
	printf("\n📝 Step 1: Enter your data\n");
	printf("💬 Please type the text you want to write to the card: ");
	scanf("%s", data);
	
	printf("\n📡 Step 2: Place your card\n");
	printf("🔄 Please place the RFID card near the sensor to write data...\n");
	
    while (1)
    {
        /* code */
        status=write_card_data(data);
		if(status==MI_OK)
		{
			printf("✅ SUCCESS! Data written successfully!\n");
			printf("📄 Written content: '%s'\n", data);
			printf("-----------------------------------------------\n");
			break;
		}
    }
    
    return 0;
}

void print_info(unsigned char *p,int cnt)
{
  int i;
	for(i=0;i<cnt;i++)
	{
		printf("%c",p[i]);
	}
	printf("\r\n");
}

 
int read_card()
{
	unsigned char CT[2];
	uint8_t status=1;
	status=PcdRequest(PICC_REQIDL ,CT);
	
	if(status==MI_OK)
	{
	  status=MI_ERR;
	  status=PcdAnticoll(SN); 
		
		printf("📱 Card detected! Type: ");
		if(CT[0] == 0x44)
		{
			printf("Mifare_UltraLight \r\n");
		}
		else if(CT[0]==0x4)
		{
			printf("MFOne_S50 \r\n");
		}
		else if(CT[0]==0X2)
		{
			printf("MFOne_S70 \r\n");
		}
		else if (CT[0]==0X8)
		{
			printf("Mifare_Pro(X)\r\n");
		}
		
		printf("Card ID: 0x");
	  	printf("%X%X%X%X\r\n",SN[0],SN[1],SN[2],SN[3]);
	}
	if(status==MI_OK)
	{
		status=MI_ERR;	
		status =PcdSelect(SN);	
	}
	  return status;
}

int card_passworld(uint8_t auth_mode,uint8_t addr,uint8_t *Src_Key,uint8_t *New_Key,uint8_t *pSnr)
{
		int status;
	
    status=read_card(); 
	
		if(status==MI_OK)
		{
			status=PcdAuthState(auth_mode,addr,Src_Key,pSnr);   
	  }

		if(status==MI_OK)
		{
		   status=PcdWrite(addr,New_Key); 
		}
		return status;
}

uint8_t write_card_data(uint8_t *data)
{
	uint8_t KEY[6]={0xff,0xff,0xff,0xff,0xff,0xff}; 
	
	  int status=MI_ERR;
	  
    status=read_card();  
	   
	
		if(status==MI_OK)
		{
			 status=PcdAuthState(PICC_AUTHENT1A,3,KEY,SN);   
			
		}
		
		if(status==MI_OK)
		{
		   status=PcdWrite(2,data); 
		}
		if(status==MI_OK)
		{
			printf("🔄 Writing data: ");
			print_info(data,16);
		}
		return status;
}

uint8_t read_card_data()
{
	 uint8_t KEY[6]={0xff,0xff,0xff,0xff,0xff,0xff}; 
	 int status;
	 uint8_t data[16];
	 
    status=read_card(); 
	
		if(status==MI_OK)
		{
			status=PcdAuthState(PICC_AUTHENT1A,3,KEY,SN);  
		}
	
		if(status==MI_OK)
		{
		   status=PcdRead(2,data); 
		}
		if(status==MI_OK)
		{
				printf("Data: ");
				print_info(data,16);
		}
		return status;
}



/*
* Team Id: 100
* Author List: Abhishek Goel, Praveen Pandey
* Filename: main.c
* Theme: Thirsty Crow
* Functions: ADC_Conversion, adc_init, adc_pin_conifg, backward, buzzer_on, buffer_off, buzzer_pin_config, forward, init_devices, left, main,
  magnet_on, magnet_off, magnet_pin_config, motor_pin_config, port_init, right, soft_left, soft_right, stop, uart0_init, uart_tx , uart_rx, ISR
* Global Variables: data, ADC_value, Right_white_line, Left_white_line, Centre_white_line
*/

#define F_CPU 14745600
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <math.h> 
#define RX  (1<<4)
#define TX  (1<<3)
#define TE  (1<<5)
#define RE  (1<<7)

/*
* Function Name:magnet_pin_config
* Input: None
* Output: None
* Logic: Used to initialize the pin values for magnet
* Example Call: magnet_pin_config()
*/
void magnet_pin_config()
{
	DDRH = 0xff ; 	// Turning pins of Port H as output pins
	PORTH = 0 ;    // Giving low(0) output from Pins in Port H
}

/*
* Function Name:buzzer_pin_config
* Input: None
* Output: None
* Logic: Used to initialize the pin values for buzzer
* Example Call: buzzer_pin_config()
*/
void buzzer_pin_config()
{
	DDRB = 0xff;
	PORTB = 0;	
} 
/*
* Function Name:motor_pin_config
* Input: None
* Output: None
* Logic: Used to initialize the pin values for motor
* Example Call: motor_pin_config()
*/
void motor_pin_config()
{
	DDRA = 0xff ;  // Turning pins of Port A as output pins
	PORTA = 0 ;   // Giving low(0) output from Pins in Port A
}

/*
* Function Name:magnet_on
* Input: None
* Output: None
* Logic: Used to Energize the magnet by the pin value to high 
* Example Call: magnet_on()
*/
void magnet_on()
{
	PORTH = 0x01 ; //Turning the output of porth0 as 1 to turn on magnet
}

/*
* Function Name:magnet_off
* Input: None
* Output: None
* Logic: Used to De-energize the magnet by the pin value to low
* Example Call: magnet_off()
*/
void magnet_off()
{
	PORTH = 0 ;  //Turning the output of porth0 as 0 to turn off manget
}
/*
* Function Name:backward
* Input: None
* Output: None
* Logic: Used to move the bot backwards by setting the pin values
* Example Call: backward()
*/
void backward()
{
	PORTA =0x05  ; //Turning on porta0 and porta2 on to move motors backwards (0000 0101)
}
/*
* Function Name:forward
* Input: None
* Output: None
* Logic: Used to move the bot forwards by setting the pin values
* Example Call: forward()
*/
void forward()
{
	PORTA = 0x0a; //Turning on porta1 and porta3 on to move motors forward (0000 1010)
}
/*
* Function Name:left
* Input: None
* Output: None
* Logic: Used to move the bot left by setting the pin values
* Example Call: left()
*/
void left()
{
	PORTA = 0x09; //Turning on porta0 and porta3 on to move motors left (0000 1001)
}
/*
* Function Name:right
* Input: None
* Output: None
* Logic: Used to move the bot right by setting the pin values
* Example Call: right()
*/
void right()
{
	PORTA = 0x06;//Turning on porta1 and porta2 on to move motors right (0000 0110)
}
/*
* Function Name:soft_left
* Input: None
* Output: None
* Logic: Used to move the bot soft left by setting the pin values
* Example Call: soft_left()
*/
void soft_left()
{
	PORTA = 0x08;//Turning on porta3 on to move motors soft left (0000 1000)
}
/*
* Function Name:soft_right
* Input: None
* Output: None
* Logic: Used to move the bot soft_right by setting the pin values
* Example Call: soft_right()
*/
void soft_right()
{
	PORTA = 0x02; //Turning on porta1 on to move motors soft right (0000 0010)
}
/*
* Function Name:stop
* Input: None
* Output: None
* Logic: Used to stop the bot by setting the pin values
* Example Call: stop()
*/
void stop()
{
	PORTA = 0 ;//Stopping motors by setting output as 0
}
/*
* Function Name:buzzer_on
* Input: None
* Output: None
* Logic: Used to start buzzer by setting the pin values
* Example Call: buzzer_on()
*/
void buzzer_on()
{
	PORTB=0xff;	
}
/*
* Function Name:buzzer_off
* Input: None
* Output: None
* Logic: Used to turn off buzzer by setting the pin values
* Example Call: buzzer_off()
*/
void buzzer_off()
{
	PORTB=0;
}
void port_init();
void timer5_init();
void velocity(unsigned char, unsigned char);
void motors_delay();


volatile unsigned char data;
unsigned char ADC_Conversion(unsigned char);
unsigned char ADC_Value;
unsigned char Left_white_line = 0;
unsigned char Center_white_line = 0;
unsigned char Right_white_line = 0;

/*
* Function Name:uart0_init
* Input: None
* Output: None
* Logic: register initialization for uart
* Example Call: uart0_init()
*/
void uart0_init()
{
	UCSR0B = 0x00;							//disable while setting baud rate
	UCSR0A = 0x00;
	UCSR0C = 0x06;
	UBRR0L = 0x5F; 							//9600BPS at 14745600Hz
	UBRR0H = 0x00;
	UCSR0B = 0x98;
	UCSR0C = 3<<1;							//setting 8-bit character and 1 stop bit
	UCSR0B = RX | TX;
}

/*
* Function Name:uart_tx
* Input: None
* Output: None
* Logic: Transmit data from usart connection
* Example Call: uart_tx()
*/
void uart_tx(char data)
{
	while(!(UCSR0A & TE));						//waiting to transmit
	UDR0 = data;
}

/*
* Function Name:uart_rx
* Input: None
* Output: None
* Logic: Transmit recieve from usart connection
* Example Call: uart_rx()
*/
unsigned char uart_rx()
{
	while(!(UCSR0A & RE));						//waiting to receive
	return UDR0;
}

/*
* Function Name:ISR
* Input: None
* Output: None
* Logic: Interrupt service routine
*/
ISR(USART0_RX_vect)
{
	data = UDR0;
}
/*
* Function Name:adc_pin_config
* Input: None
* Output: None
* Logic: pin configuration for analog to digital conversion
* Example Call: adc_pin_config()
*/
void adc_pin_config (void)
{
 DDRF = 0x00; 
 PORTF = 0x00;
}
/*
* Function Name:port_init
* Input: None
* Output: None
* Logic: initialize all the pin configurations
* Example Call: port_nit()
*/
void port_init()
{
	adc_pin_config();
	uart0_init();
	motor_pin_config();
	magnet_pin_config();
	buzzer_pin_config();
}

/*
* Function Name:adc_init
* Input: None
* Output: None
* Logic: adc register configuration initialization
* Example Call: adc_init()
*/
void adc_init()
{
	ADCSRA = 0x00;
	ADCSRB = 0x00;		//MUX5 = 0
	ADMUX = 0x20;		//Vref=5V external --- ADLAR=1 --- MUX4:0 = 0000
	ACSR = 0x80;
	ADCSRA = 0x86;		//ADEN=1 --- ADIE=1 --- ADPS2:0 = 1 1 0
}
/*
* Function Name:ADC_Conversion
* Input: None
* Output: None
* Logic: Function For ADC Conversion
* Example Call: ADC_Conversion()
*/
unsigned char ADC_Conversion(unsigned char Ch) 
{
	unsigned char a;
	if(Ch>7)
	{
		ADCSRB = 0x08;
	}
	Ch = Ch & 0x07;  			
	ADMUX= 0x20| Ch;	   		
	ADCSRA = ADCSRA | 0x40;		//Set start conversion bit
	while((ADCSRA&0x10)==0);	//Wait for conversion to complete
	a=ADCH;
	ADCSRA = ADCSRA|0x10; //clear ADIF (ADC Interrupt Flag) by writing 1 to it
	ADCSRB = 0x00;
	return a;
}
/*
* Function Name:init_devices
* Input: None
* Output: None
* Logic: Function For initializing all the devices by calling their pin configuration funtion
* Example Call: init_devices()
*/
void init_devices (void)
{
 	cli(); //Clears the global interrupts
	port_init();
	adc_init();
	sei();   //Enables the global interrupts
}
/*
* Function Name:Main
* Input: None
* Output: None
* Logic: The main function receives a command from the python script and decides the action by a list of given functions 
* Example Call: ADC_Conversion()
*/
int main()
{
	init_devices();
	char a=' ';
	while(1)
	{
		a=uart_rx();
		Left_white_line = ADC_Conversion(1);	//Getting data of Left WL Sensor
		Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
		Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
		switch (a)
		{
			case 'b':buzzer_on();
					 break;
			case 'n':buzzer_off();
					 break;
			case 'm':magnet_on();
					 break;
			case 'o':magnet_off();
					 break;
			case 'y':left();
					break;
			case 'u':right();
					 break;
			case 'z':backward();
					break;
			case 'k':left();
					 while(1)
					 {
						Left_white_line = ADC_Conversion(1);	//Getting data of Left WL Sensor
						Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
						if(Left_white_line<200 && Center_white_line<200 && Right_white_line<200)
						{
							stop();
							break;
						}
					 }
					 break;
			case 'w':forward();
					while(1)
					 {
						 Left_white_line = ADC_Conversion(1);	//Gettinwwg data of Left WL Sensor
						 Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						 Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
						 
						if(Left_white_line>200 && Center_white_line<200 && Right_white_line<200)
						{
							soft_left();
							if(Left_white_line<200 && Center_white_line>200 && Right_white_line<200)
							{
								forward();								
							}
					
						}	 
						else if(Left_white_line<200 && Center_white_line<200 && Right_white_line>200)
						{
							soft_right();
							if(Left_white_line<200 && Center_white_line>200 && Right_white_line<200)
							{
								forward();
							}
							
						}
						else if(Left_white_line>200 && Center_white_line>200 && Right_white_line>200)
						{
							stop();
							uart_tx('o');
							break;
						}							
						else if(Left_white_line<200 && Center_white_line>200 && Right_white_line<200)
						{
							forward();
						}
						else if(Left_white_line>200 &&Center_white_line>200 && Right_white_line<200)
						{
							soft_left();
							if(Left_white_line<200 && Center_white_line>200 && Right_white_line<200)
							{
								forward();
							}
						}
						else if(Left_white_line<200 &&Center_white_line>200 && Right_white_line>200)
						{
							soft_right();
							if(Left_white_line<200 && Center_white_line>200 && Right_white_line<200)
							{
								forward();
							}
						}							
					 }	
					 break;
			case 'a':	forward();
						while(1)
						{
						 Left_white_line=ADC_Conversion(1);							
						 Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						 Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
						 if(Left_white_line<200 && Right_white_line<200 && Center_white_line<200)
						 {
							stop();
							break;							 
						 }	
						}
						left();
						while(1)
						{	
						 Left_white_line = ADC_Conversion(1);	//Getting data of Left WL Sensor
						 Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						 Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
							if(Center_white_line>200 && Left_white_line<200 && Right_white_line<200)
							{
								stop();
								uart_tx('o');
								break;
							}								
						}
						break;										
			case 's':backward();
					 while(1)
					{
						Left_white_line=ADC_Conversion(1);
						Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
						if(Left_white_line>200 && Right_white_line>200 && Center_white_line>200)
						{
							stop();
							break;
						}
					}
					break;
			case 'f':forward();	
					break;		
			case 'd':forward();
					while(1)
					{
						Left_white_line=ADC_Conversion(1);
						Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
						if(Left_white_line<200 && Right_white_line<200 && Center_white_line<200)
						{
							stop();
							break;
						}
					}
					right();
					while(1)
					{
						
						 Left_white_line = ADC_Conversion(1);	//Getting data of Left WL Sensor
						 Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
						 Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
						if(Center_white_line>200 && Left_white_line<200 && Right_white_line<200)
						{
							stop();
							uart_tx('o');
							break;
						}
					}
					break;
			case 'r':right();
			while(1)
			{
				Left_white_line = ADC_Conversion(1);	//Getting data of Left WL Sensor
				Center_white_line = ADC_Conversion(2);	//Getting data of Center WL Sensor
				Right_white_line = ADC_Conversion(3);	//Getting data of Right WL Sensor
				if(Left_white_line<200 && Center_white_line<200 && Right_white_line<200)
				{
					stop();
					break;
				}
			}
			break;
			default: stop();	
		}
	}
}
















#include <Ethernet.h> //Load Ethernet Library
#include <EthernetUdp.h> //Load UDP Library
#include <SPI.h> //Load the SPI Library
 
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(10, 2, 1, 50); //Assign my IP adress
unsigned int localPort = 8888; //Assign a Port to talk over
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
String datReq; //String for our data
int packetSize; //Size of Packet
EthernetUDP Udp; //Define UDP Object
 
void setup() {
  
Serial.begin(9600); //Turn on Serial Port
Ethernet.begin(mac, ip); //Initialize Ethernet
Udp.begin(localPort); //Initialize Udp
delay(1500); //delay

pinMode(8,INPUT);
pinMode(7,INPUT);
pinMode(6,INPUT);
pinMode(5,INPUT);

pinMode(31, INPUT);

}
 
void loop() {
  
  packetSize = Udp.parsePacket(); //Read theh packetSize
  
  if(packetSize>0){ //Check to see if a request is present
  
    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE); //Reading the data request on the Udp
    String datReq(packetBuffer); //Convert packetBuffer array to string datReq
    
    int Sensor[5];

    Sensor[0] = digitalRead(8);
    Sensor[1] = digitalRead(7);
    Sensor[2] = digitalRead(6);
    Sensor[3] = digitalRead(5);
    Sensor[4] = digitalRead(31);
    
    //int InfraRed = digitalRead(31);
    
    char Data[5];
    
    int i;
    int result = 0;
    int mult = 1;
    for (i=0;i<5;i++){
      result = result + (Sensor[i]*mult);
      mult = mult * 2;
    }
    sprintf(Data,"%d",result);
    

    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());  //Initialize Packet send
    Udp.print(Data); //Send string back to client 
    Udp.endPacket(); //Packet has been sent 

  }
  memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE);
}


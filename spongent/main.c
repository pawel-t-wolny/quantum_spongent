/*
	* SPONGENT hash function - Implementation
	* This code is placed in the public domain
	* For more information, feedback or questions, please refer to our website:
	* https://sites.google.com/site/spongenthash/

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "spongent.h"



int main(int argc, char *argv[])
{

	int i;
  
BitSequence message[256] = {'d', 'u', 'p', 'a'};

if (argc>1) {
	for (i = 0; i < strlen(argv[1]); i++)
	{
		message[i] = argv[1][i];
	}
}

	BitSequence hashval[hashsize / 8] = { 0 };

//	BitSequence message[256] = "";

  
	DataLength databitlen = sizeof(message);

	printf("Message(String)\t:%s\n", message);
	printf("Message(Hex)\t:");
	for (i = 0; i < databitlen / 8; i++) {
		printf("%02X", message[i]);
	}
	printf("\n");



	SpongentHash(message, databitlen, hashval);

	printf("Hash\t\t:");
	for (i = 0; i<hashsize / 8; i++)
		printf("%.2X", hashval[i]);
	printf("\n");
		
	return 0;
}
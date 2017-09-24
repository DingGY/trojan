// sockettest.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"


#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <Winerror.h>
#include <stdlib.h>   // Needed for _wtoi


#pragma comment(lib,"ws2_32.lib")
#define IP_LOCAL "192.168.1.104"
#define IP_REMOTE "192.168.18.132"
#define PORT 6789
int main()
{
	int ret;
	//socket
	WORD wVersionRequested = MAKEWORD(2, 2);
	WSADATA wsaData;
	SOCKET ClientSocket,RemoteSocket;
	struct sockaddr_in ClientAddr,RemoteAddr;
	char buffer[4096] = { 0 };
	DWORD bytesRead;
	if (WSAStartup(MAKEWORD(2, 2), &wsaData))
	{
		printf("WSAStartup failed\n");
		WSACleanup();
		return 1;
	}
	ClientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (ClientSocket == INVALID_SOCKET)
	{
		printf("create socket failed:%d\n", GetLastError());
		WSACleanup();
		return -1;
	}

	ClientAddr.sin_family = AF_INET;
	ClientAddr.sin_addr.s_addr = inet_addr(IP_LOCAL);
	ClientAddr.sin_port = htons(PORT);

	ret = bind(ClientSocket, (struct sockaddr*)&ClientAddr, sizeof(ClientAddr));
	if (ret == SOCKET_ERROR)
	{
		printf("bind Error::%d\n", GetLastError());
		return -1;

	}
	if (listen(ClientSocket,5) == SOCKET_ERROR)
	{
		printf("listen Error::%d\n", GetLastError());
		return -1;
	}

	sprintf(buffer,"getint");
	int len;
	len = sizeof(RemoteAddr);
	int count = 0;
	while (true)
	{
		if (count == 0)
		{
			RemoteSocket = accept(ClientSocket, (struct sockaddr*)&RemoteAddr, (int*)&len);
		}
		
		if (RemoteSocket == INVALID_SOCKET)
		{
			printf("accept::%d\n", GetLastError());
			return -1;
		}
		ret = send(RemoteSocket, buffer, (int)strlen(buffer), 0);
		if (ret == SOCKET_ERROR)
		{
			printf("Send Info Error::%d\n", GetLastError());
			return -1;
		}
		count++;
	}
	
    return 0;
}


//#define WIN32_LEAN_AND_MEAN
//
//#include <windows.h>
//#include <winsock2.h>
//#include <ws2tcpip.h>
//#include <stdio.h>
//
//// Need to link with Ws2_32.lib
//#pragma comment(lib, "ws2_32.lib")
//
//
//int __cdecl main()
//{
//
//	WORD wVersionRequested;
//	WSADATA wsaData;
//	int err;
//
//	/* Use the MAKEWORD(lowbyte, highbyte) macro declared in Windef.h */
//	wVersionRequested = MAKEWORD(2, 2);
//
//	err = WSAStartup(wVersionRequested, &wsaData);
//	if (err != 0) {
//		/* Tell the user that we could not find a usable */
//		/* Winsock DLL.                                  */
//		printf("WSAStartup failed with error: %d\n", err);
//		return 1;
//	}
//	SOCKET ClientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
//	if (ClientSocket == INVALID_SOCKET)
//	{
//		printf("create socket failed:%d\n", GetLastError());
//		WSACleanup();
//		return -1;
//	}
//	/* Confirm that the WinSock DLL supports 2.2.*/
//	/* Note that if the DLL supports versions greater    */
//	/* than 2.2 in addition to 2.2, it will still return */
//	/* 2.2 in wVersion since that is the version we      */
//	/* requested.                                        */
//
//	if (LOBYTE(wsaData.wVersion) != 2 || HIBYTE(wsaData.wVersion) != 2) {
//		/* Tell the user that we could not find a usable */
//		/* WinSock DLL.                                  */
//		printf("Could not find a usable version of Winsock.dll\n");
//		WSACleanup();
//		return 1;
//	}
//	else
//		printf("The Winsock 2.2 dll was found okay\n");
//
//
//	/* The Winsock DLL is acceptable. Proceed to use it. */
//
//	/* Add network programming using Winsock here */
//
//	/* then call WSACleanup when done using the Winsock dll */
//
//	WSACleanup();
//
//}

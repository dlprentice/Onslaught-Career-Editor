/* address: 0x0056928f */
/* name: CRT__ReportRuntimeError */
/* signature: void __cdecl CRT__ReportRuntimeError(int param_1) */


void __cdecl CRT__ReportRuntimeError(int param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  DWORD DVar3;
  size_t sVar4;
  HANDLE hFile;
  int iVar5;
  CHAR *_Dest;
  char acStackY_1e3 [7];
  LPCVOID lpBuffer;
  LPDWORD lpNumberOfBytesWritten;
  LPOVERLAPPED lpOverlapped;
  CHAR local_1a8 [260];
  undefined1 local_a4 [160];

  iVar5 = 0;
  piVar2 = &DAT_00656130;
  do {
    if (param_1 == *piVar2) break;
    piVar2 = piVar2 + 2;
    iVar5 = iVar5 + 1;
  } while ((int)piVar2 < 0x6561c0);
  if (param_1 == (&DAT_00656130)[iVar5 * 2]) {
    if ((DAT_009d0914 == 1) || ((DAT_009d0914 == 0 && (DAT_00653644 == 1)))) {
      lpNumberOfBytesWritten = (LPDWORD)&param_1;
      puVar1 = (undefined4 *)(iVar5 * 8 + 0x656134);
      lpOverlapped = (LPOVERLAPPED)0x0;
      sVar4 = _strlen((char *)*puVar1);
      lpBuffer = (LPCVOID)*puVar1;
      hFile = GetStdHandle(0xfffffff4);
      WriteFile(hFile,lpBuffer,sVar4,lpNumberOfBytesWritten,lpOverlapped);
    }
    else if (param_1 != 0xfc) {
      DVar3 = GetModuleFileNameA((HMODULE)0x0,local_1a8,0x104);
      if (DVar3 == 0) {
        CDXTexture__Helper_00567de0(local_1a8,"<program name unknown>");
      }
      _Dest = local_1a8;
      sVar4 = _strlen(local_1a8);
      if (0x3c < sVar4 + 1) {
        sVar4 = _strlen(local_1a8);
        _Dest = acStackY_1e3 + sVar4;
        _strncpy(_Dest,&DAT_0063fb70,3);
      }
      CDXTexture__Helper_00567de0(local_a4,"Runtime Error!\n\nProgram: ");
      CDXTexture__Helper_00567df0(local_a4,_Dest);
      CDXTexture__Helper_00567df0(local_a4,&DAT_005e6154);
      CDXTexture__Helper_00567df0(local_a4,*(void **)(iVar5 * 8 + 0x656134));
      acStackY_1e3[3] = -0x4d;
      acStackY_1e3[4] = -0x6d;
      acStackY_1e3[5] = 'V';
      acStackY_1e3[6] = '\0';
      CDXTexture__Helper_0056d25e((int)local_a4,0x5e612c,0x12010);
    }
  }
  return;
}

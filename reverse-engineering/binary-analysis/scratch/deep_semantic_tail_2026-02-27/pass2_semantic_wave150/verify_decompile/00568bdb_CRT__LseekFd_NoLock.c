/* address: 0x00568bdb */
/* name: CRT__LseekFd_NoLock */
/* signature: int __cdecl CRT__LseekFd_NoLock(uint param_1, int param_2, int param_3) */


int __cdecl CRT__LseekFd_NoLock(uint param_1,int param_2,int param_3)

{
  byte *pbVar1;
  HANDLE hFile;
  undefined4 *puVar2;
  DWORD DVar3;
  uint uVar4;

  hFile = (HANDLE)CDXTexture__Helper_0056b212(param_1);
  if (hFile == (HANDLE)0xffffffff) {
    puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar2 = 9;
  }
  else {
    DVar3 = SetFilePointer(hFile,param_2,(PLONG)0x0,param_3);
    if (DVar3 == 0xffffffff) {
      uVar4 = GetLastError();
    }
    else {
      uVar4 = 0;
    }
    if (uVar4 == 0) {
      pbVar1 = (byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24);
      *pbVar1 = *pbVar1 & 0xfd;
      return DVar3;
    }
    CTexture__Helper_00567a35(uVar4);
  }
  return -1;
}

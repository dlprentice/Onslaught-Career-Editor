/* address: 0x0056b2d5 */
/* name: CRT__CommitFileHandle */
/* signature: int __cdecl CRT__CommitFileHandle(uint param_1) */


int __cdecl CRT__CommitFileHandle(uint param_1)

{
  HANDLE hFile;
  BOOL BVar1;
  DWORD DVar2;
  DWORD *pDVar3;
  undefined4 *puVar4;
  int iVar5;

  if (DAT_009d33a0 <= param_1) {
LAB_0056b356:
    puVar4 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar4 = 9;
    return -1;
  }
  iVar5 = (param_1 & 0x1f) * 0x24;
  if ((*(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + iVar5) & 1) == 0) goto LAB_0056b356;
  CRT__LockFileHandleByIndex(param_1);
  if ((*(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + iVar5) & 1) != 0) {
    hFile = (HANDLE)CRT__GetOsFileHandleByIndex(param_1);
    BVar1 = FlushFileBuffers(hFile);
    if (BVar1 == 0) {
      DVar2 = GetLastError();
    }
    else {
      DVar2 = 0;
    }
    iVar5 = 0;
    if (DVar2 == 0) goto LAB_0056b34b;
    pDVar3 = (DWORD *)CTexture__Helper_00567ab1();
    *pDVar3 = DVar2;
  }
  puVar4 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar4 = 9;
  iVar5 = -1;
LAB_0056b34b:
  CRT__UnlockFileHandleByIndex(param_1);
  return iVar5;
}

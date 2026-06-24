/* address: 0x0056db76 */
/* name: CDXTexture__Helper_0056db76 */
/* signature: int __cdecl CDXTexture__Helper_0056db76(uint param_1, int param_2) */


int __cdecl CDXTexture__Helper_0056db76(uint param_1,int param_2)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int *piVar5;
  undefined4 *puVar6;
  HANDLE hFile;
  BOOL BVar7;
  DWORD DVar8;
  DWORD *pDVar9;
  int iVar10;
  uint uVar11;
  undefined1 local_1008 [4064];
  undefined4 uStackY_28;

  CRT__AllocaProbe();
  iVar10 = 0;
  iVar1 = CRT__LseekFd_NoLock(param_1,0,1);
  if ((iVar1 == -1) || (iVar2 = CRT__LseekFd_NoLock(param_1,0,2), iVar2 == -1)) {
    iVar10 = -1;
  }
  else {
    uVar11 = param_2 - iVar2;
    if ((int)uVar11 < 1) {
      if ((int)uVar11 < 0) {
        CRT__LseekFd_NoLock(param_1,param_2,0);
        hFile = (HANDLE)CRT__GetOsFileHandleByIndex(param_1);
        BVar7 = SetEndOfFile(hFile);
        iVar10 = (BVar7 != 0) - 1;
        if (iVar10 == -1) {
          puVar6 = (undefined4 *)CTexture__Helper_00567aa8();
          *puVar6 = 0xd;
          DVar8 = GetLastError();
          pDVar9 = (DWORD *)CTexture__Helper_00567ab1();
          *pDVar9 = DVar8;
        }
      }
    }
    else {
      _memset(local_1008,0,0x1000);
      uStackY_28 = 0x56dbe3;
      iVar2 = CDXTexture__Helper_0056e2ee(param_1,0x8000);
      do {
        uVar3 = 0x1000;
        if ((int)uVar11 < 0x1000) {
          uVar3 = uVar11;
        }
        iVar4 = CRT__WriteFdTextMode_NoLock(param_1,local_1008,uVar3);
        if (iVar4 == -1) {
          piVar5 = (int *)CTexture__Helper_00567ab1();
          if (*piVar5 == 5) {
            puVar6 = (undefined4 *)CTexture__Helper_00567aa8();
            *puVar6 = 0xd;
          }
          iVar10 = -1;
          break;
        }
        uVar11 = uVar11 - iVar4;
      } while (0 < (int)uVar11);
      CDXTexture__Helper_0056e2ee(param_1,iVar2);
    }
    CRT__LseekFd_NoLock(param_1,iVar1,0);
  }
  return iVar10;
}

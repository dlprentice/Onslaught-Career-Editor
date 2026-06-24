/* address: 0x00564fdf */
/* name: CRT__FlushOrCloseAllFileHandles */
/* signature: int __cdecl CRT__FlushOrCloseAllFileHandles(int param_1) */


int __cdecl CRT__FlushOrCloseAllFileHandles(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;

  iVar2 = 0;
  iVar4 = 0;
  CDXTexture__Helper_00561179(2);
  iVar3 = 0;
  if (0 < DAT_009d4600) {
    do {
      iVar1 = *(int *)(DAT_009d35f8 + iVar3 * 4);
      if ((iVar1 != 0) && ((*(byte *)(iVar1 + 0xc) & 0x83) != 0)) {
        CRT__LockRouteByIndex(iVar3,iVar1);
        iVar1 = *(int *)(DAT_009d35f8 + iVar3 * 4);
        if ((*(uint *)(iVar1 + 0xc) & 0x83) != 0) {
          if (param_1 == 1) {
            iVar1 = CTexture__Helper_00564f4c(iVar1);
            if (iVar1 != -1) {
              iVar2 = iVar2 + 1;
            }
          }
          else if ((param_1 == 0) && ((*(uint *)(iVar1 + 0xc) & 2) != 0)) {
            iVar1 = CTexture__Helper_00564f4c(iVar1);
            if (iVar1 == -1) {
              iVar4 = -1;
            }
          }
        }
        CRT__UnlockRouteByIndex(iVar3,*(int *)(DAT_009d35f8 + iVar3 * 4));
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 < DAT_009d4600);
  }
  CTexture__Helper_005611da(2);
  if (param_1 != 1) {
    iVar2 = iVar4;
  }
  return iVar2;
}

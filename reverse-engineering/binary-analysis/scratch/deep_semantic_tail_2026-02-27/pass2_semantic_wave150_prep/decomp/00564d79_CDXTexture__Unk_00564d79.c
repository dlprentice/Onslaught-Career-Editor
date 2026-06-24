/* address: 0x00564d79 */
/* name: CDXTexture__Unk_00564d79 */
/* signature: int CDXTexture__Unk_00564d79(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_00564d79(void)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  undefined4 *puVar4;

  puVar4 = (undefined4 *)0x0;
  CDXTexture__Helper_00561179(2);
  iVar3 = 0;
  if (0 < DAT_009d4600) {
    do {
      iVar1 = *(int *)(DAT_009d35f8 + iVar3 * 4);
      if (iVar1 == 0) {
        iVar3 = iVar3 * 4;
        pvVar2 = _malloc(0x38);
        *(void **)(iVar3 + DAT_009d35f8) = pvVar2;
        if (*(int *)(iVar3 + DAT_009d35f8) != 0) {
          InitializeCriticalSection((LPCRITICAL_SECTION)(*(int *)(iVar3 + DAT_009d35f8) + 0x20));
          EnterCriticalSection((LPCRITICAL_SECTION)(*(int *)(iVar3 + DAT_009d35f8) + 0x20));
          puVar4 = *(undefined4 **)(iVar3 + DAT_009d35f8);
LAB_00564e1d:
          if (puVar4 != (undefined4 *)0x0) {
            puVar4[4] = 0xffffffff;
            puVar4[1] = 0;
            puVar4[3] = 0;
            puVar4[2] = 0;
            *puVar4 = 0;
            puVar4[7] = 0;
          }
        }
        break;
      }
      if ((*(byte *)(iVar1 + 0xc) & 0x83) == 0) {
        CRT__LockRouteByIndex(iVar3,iVar1);
        iVar1 = *(int *)(DAT_009d35f8 + iVar3 * 4);
        if ((*(byte *)(iVar1 + 0xc) & 0x83) == 0) {
          puVar4 = *(undefined4 **)(DAT_009d35f8 + iVar3 * 4);
          goto LAB_00564e1d;
        }
        CRT__UnlockRouteByIndex(iVar3,iVar1);
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 < DAT_009d4600);
  }
  CTexture__Helper_005611da(2);
  return (int)puVar4;
}

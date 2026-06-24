/* address: 0x005d08ad */
/* name: CDXTexture__Helper_005d08ad */
/* signature: int CDXTexture__Helper_005d08ad(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_005d08ad(void)

{
  undefined4 *puVar1;
  uint uVar2;
  int *piVar3;
  int iVar4;
  uint *puVar5;

  CRT__LockByIndex(3);
  if (DAT_009d3038 == '\0') {
    init_namebuf(1);
LAB_005d08dc:
    puVar1 = (undefined4 *)CRT__AcquireFileStreamSlot();
    if (puVar1 != (undefined4 *)0x0) {
      uVar2 = CRT__OpenFd(0x9d3038,0x8542,0x40,0x180);
      if (uVar2 == 0xffffffff) {
        do {
          piVar3 = (int *)CTexture__Helper_00567aa8();
          if (*piVar3 != 0x11) break;
          iVar4 = CRT__IncrementDotSuffixCounter(&DAT_009d3038);
          if (iVar4 != 0) break;
          uVar2 = CRT__OpenFd(0x9d3038,0x8542,0x40,0x180);
        } while (uVar2 == 0xffffffff);
        if (uVar2 != 0xffffffff) goto LAB_005d0936;
      }
      else {
LAB_005d0936:
        puVar5 = CRT__StrDup(&DAT_009d3038);
        puVar1[7] = puVar5;
        if (puVar5 != (uint *)0x0) {
          puVar1[1] = 0;
          *puVar1 = 0;
          puVar1[2] = 0;
          puVar1[3] = DAT_009d0ad4 | 0x80;
          puVar1[4] = uVar2;
          CRT__UnlockRouteByAddress((uint)puVar1);
          goto LAB_005d0974;
        }
        CRT__CloseFd(uVar2);
      }
      CRT__UnlockRouteByAddress((uint)puVar1);
    }
  }
  else {
    iVar4 = CRT__IncrementDotSuffixCounter(&DAT_009d3038);
    if (iVar4 == 0) goto LAB_005d08dc;
  }
  puVar1 = (undefined4 *)0x0;
LAB_005d0974:
  CTexture__Helper_005611da(3);
  return (int)puVar1;
}

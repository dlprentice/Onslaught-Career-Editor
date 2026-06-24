/* address: 0x0056aff4 */
/* name: CRT__AllocOsHandleSlot */
/* signature: int CRT__AllocOsHandleSlot(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__AllocOsHandleSlot(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int *piVar3;
  uint uVar4;
  int local_8;
  int local_4;

  uVar4 = 0xffffffff;
  CDXTexture__Helper_00561179(0x12);
  local_8 = 0;
  local_4 = 0;
  piVar3 = &DAT_009d32a0;
  while (puVar2 = (undefined4 *)*piVar3, puVar1 = puVar2, puVar2 != (undefined4 *)0x0) {
    for (; puVar2 < puVar1 + 0x120; puVar2 = puVar2 + 9) {
      if ((*(byte *)(puVar2 + 1) & 1) == 0) {
        if (puVar2[2] == 0) {
          CDXTexture__Helper_00561179(0x11);
          if (puVar2[2] == 0) {
            InitializeCriticalSection((LPCRITICAL_SECTION)(puVar2 + 3));
            puVar2[2] = puVar2[2] + 1;
          }
          CTexture__Helper_005611da(0x11);
        }
        EnterCriticalSection((LPCRITICAL_SECTION)(puVar2 + 3));
        if ((*(byte *)(puVar2 + 1) & 1) == 0) {
          *puVar2 = 0xffffffff;
          uVar4 = ((int)puVar2 - *piVar3) / 0x24 + local_4;
          if (uVar4 != 0xffffffff) goto LAB_0056b106;
          break;
        }
        LeaveCriticalSection((LPCRITICAL_SECTION)(puVar2 + 3));
      }
      puVar1 = (undefined4 *)*piVar3;
    }
    local_4 = local_4 + 0x20;
    piVar3 = piVar3 + 1;
    local_8 = local_8 + 1;
    if (0x9d339f < (int)piVar3) goto LAB_0056b106;
  }
  puVar2 = _malloc(0x480);
  if (puVar2 != (undefined4 *)0x0) {
    DAT_009d33a0 = DAT_009d33a0 + 0x20;
    (&DAT_009d32a0)[local_8] = puVar2;
    puVar1 = puVar2;
    for (; puVar2 < puVar1 + 0x120; puVar2 = puVar2 + 9) {
      *(undefined1 *)(puVar2 + 1) = 0;
      *puVar2 = 0xffffffff;
      puVar2[2] = 0;
      *(undefined1 *)((int)puVar2 + 5) = 10;
      puVar1 = (undefined4 *)(&DAT_009d32a0)[local_8];
    }
    uVar4 = local_8 << 5;
    CDXTexture__Helper_0056b254(uVar4);
  }
LAB_0056b106:
  CTexture__Helper_005611da(0x12);
  return uVar4;
}

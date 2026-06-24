/* address: 0x005acf90 */
/* name: CDXTexture__FinalizeScanBitstreamState */
/* signature: int CDXTexture__FinalizeScanBitstreamState(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__FinalizeScanBitstreamState(void)

{
  int iVar1;
  int iVar2;
  int unaff_ESI;
  undefined4 *puVar3;

  iVar2 = *(int *)(unaff_ESI + 0x1bc);
  iVar1 = *(int *)(unaff_ESI + 0x1c0);
  *(int *)(iVar2 + 0x18) =
       *(int *)(iVar2 + 0x18) +
       ((int)(*(int *)(iVar1 + 0x10) + (*(int *)(iVar1 + 0x10) >> 0x1f & 7U)) >> 3);
  *(undefined4 *)(iVar1 + 0x10) = 0;
  iVar2 = (**(code **)(iVar2 + 8))();
  if (iVar2 == 0) {
    return 0;
  }
  iVar2 = *(int *)(unaff_ESI + 0x14c);
  if (0 < iVar2) {
    puVar3 = (undefined4 *)(iVar1 + 0x14);
    for (; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar3 = 0;
      puVar3 = puVar3 + 1;
    }
  }
  *(undefined4 *)(iVar1 + 0x24) = *(undefined4 *)(unaff_ESI + 0x118);
  if (*(int *)(unaff_ESI + 0x1a4) == 0) {
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return 1;
}

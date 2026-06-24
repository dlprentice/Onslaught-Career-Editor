/* address: 0x005015c0 */
/* name: CEngine__Unk_005015c0 */
/* signature: void CEngine__Unk_005015c0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_005015c0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;

  for (iVar2 = DAT_00854e00; iVar2 != 0; iVar2 = *(int *)(iVar2 + 0x58)) {
    iVar1 = *(int *)(iVar2 + 0x1c);
    if (iVar1 == 0) {
      iVar3 = 0;
    }
    else {
      iVar3 = 0x400;
      if (0x400 < iVar1) {
        do {
          iVar3 = iVar3 * 2;
        } while (iVar3 < iVar1);
      }
    }
    iVar1 = *(int *)(iVar2 + 0x34);
    if (iVar1 == 0) {
      iVar4 = 0;
    }
    else {
      iVar4 = 0x400;
      if (0x400 < iVar1) {
        do {
          iVar4 = iVar4 * 2;
        } while (iVar4 < iVar1);
      }
    }
    if (iVar3 < *(int *)(iVar2 + 0x14 + *(int *)(iVar2 + 0x48) * 4)) {
      CVBufTexture__ResizeVertexBuffer(iVar3);
    }
    if (iVar4 < *(int *)(iVar2 + 0x30)) {
      CVBufTexture__ResizeIndexBuffer(iVar4);
    }
  }
  return;
}

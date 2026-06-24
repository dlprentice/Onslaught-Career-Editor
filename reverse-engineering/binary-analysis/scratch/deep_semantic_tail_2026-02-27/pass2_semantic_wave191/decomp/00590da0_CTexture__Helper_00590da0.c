/* address: 0x00590da0 */
/* name: CTexture__Helper_00590da0 */
/* signature: int CTexture__Helper_00590da0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_00590da0(void)

{
  int iVar1;
  undefined4 *puVar2;
  int *unaff_ESI;

  if (unaff_ESI[5] != 0xcc) {
    (**(code **)unaff_ESI[0x6a])();
    unaff_ESI[0x23] = 0;
    unaff_ESI[5] = 0xcc;
  }
  iVar1 = *(int *)(unaff_ESI[0x6a] + 8);
  while (iVar1 != 0) {
    puVar2 = (undefined4 *)*unaff_ESI;
    puVar2[5] = 0x30;
    (*(code *)*puVar2)();
    iVar1 = *(int *)(unaff_ESI[0x6a] + 8);
  }
  unaff_ESI[5] = (unaff_ESI[0x11] != 0) + 0xcd;
  return 1;
}

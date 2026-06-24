/* address: 0x005ad590 */
/* name: CFastVB__Unk_005ad590 */
/* signature: int CFastVB__Unk_005ad590(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Unk_005ad590(void)

{
  int iVar1;
  int iVar2;
  int unaff_EBX;
  undefined4 *puVar3;

  iVar2 = *(int *)(unaff_EBX + 0x1bc);
  iVar1 = *(int *)(unaff_EBX + 0x1c0);
  *(int *)(iVar2 + 0x18) =
       *(int *)(iVar2 + 0x18) +
       ((int)(*(int *)(iVar1 + 0x10) + (*(int *)(iVar1 + 0x10) >> 0x1f & 7U)) >> 3);
  *(undefined4 *)(iVar1 + 0x10) = 0;
  iVar2 = (**(code **)(iVar2 + 8))();
  if (iVar2 == 0) {
    return 0;
  }
  iVar2 = *(int *)(unaff_EBX + 0x14c);
  if (0 < iVar2) {
    puVar3 = (undefined4 *)(iVar1 + 0x18);
    for (; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar3 = 0;
      puVar3 = puVar3 + 1;
    }
  }
  *(undefined4 *)(iVar1 + 0x28) = *(undefined4 *)(unaff_EBX + 0x118);
  iVar2 = *(int *)(unaff_EBX + 0x1a4);
  *(undefined4 *)(iVar1 + 0x14) = 0;
  if (iVar2 == 0) {
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return 1;
}

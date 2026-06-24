/* address: 0x0040d4d0 */
/* name: CGeneralVolume__Update4ACLatchFromHeightAndA0 */
/* signature: void __fastcall CGeneralVolume__Update4ACLatchFromHeightAndA0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__Update4ACLatchFromHeightAndA0(int param_1)

{
  int iVar1;
  undefined4 uVar2;

  if (*(int *)(param_1 + 0x4ac) != 0) {
    *(undefined4 *)(param_1 + 0x5dc) = 0;
    *(undefined4 *)(param_1 + 0x4ac) = 0;
    return;
  }
  iVar1 = *(int *)(param_1 + 0x4b0);
  if ((*(float *)(iVar1 + 0x2c) <= *(float *)(param_1 + 0xfc)) &&
     (_DAT_005d856c < *(float *)(iVar1 + 0xa0))) {
    uVar2 = *(undefined4 *)(iVar1 + 0xa0);
    *(undefined4 *)(param_1 + 0x4ac) = 1;
    *(undefined4 *)(param_1 + 0x5dc) = uVar2;
  }
  return;
}

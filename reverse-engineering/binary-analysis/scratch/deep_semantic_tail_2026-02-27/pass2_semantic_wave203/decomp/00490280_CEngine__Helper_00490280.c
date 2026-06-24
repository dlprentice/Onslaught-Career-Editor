/* address: 0x00490280 */
/* name: CEngine__Helper_00490280 */
/* signature: int __fastcall CEngine__Helper_00490280(int param_1) */


int __fastcall CEngine__Helper_00490280(int param_1)

{
  int iVar1;
  undefined4 *puVar2;

  *(undefined4 *)(param_1 + 0x1c0) = 0;
  puVar2 = (undefined4 *)(param_1 + 0x1c4);
  for (iVar1 = 0xae; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  return 1;
}

/* address: 0x00490f10 */
/* name: CUnitAI__Unk_00490f10 */
/* signature: int __fastcall CUnitAI__Unk_00490f10(int param_1) */


int __fastcall CUnitAI__Unk_00490f10(int param_1)

{
  int iVar1;

  iVar1 = CFrontEndPage__Init_ReturnTrue();
  if (iVar1 == 0) {
    return 0;
  }
  *(undefined4 *)(param_1 + 0x93e0) = 0;
  *(undefined4 *)(param_1 + 0x93e4) = 0;
  return 1;
}

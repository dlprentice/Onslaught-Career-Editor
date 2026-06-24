/* address: 0x004fde10 */
/* name: CUnit__Unk_004fde10 */
/* signature: int __fastcall CUnit__Unk_004fde10(int param_1) */


int __fastcall CUnit__Unk_004fde10(int param_1)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 0x244);
  if (((iVar1 != 4) && (iVar1 != 3)) && (iVar1 != 5)) {
    return 0;
  }
  return 1;
}

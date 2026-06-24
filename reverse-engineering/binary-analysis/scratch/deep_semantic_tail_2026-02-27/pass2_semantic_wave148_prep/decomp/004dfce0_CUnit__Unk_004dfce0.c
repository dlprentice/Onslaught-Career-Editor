/* address: 0x004dfce0 */
/* name: CUnit__Unk_004dfce0 */
/* signature: int __fastcall CUnit__Unk_004dfce0(int param_1) */


int __fastcall CUnit__Unk_004dfce0(int param_1)

{
  int iVar1;

  iVar1 = CUnit__Helper_004fd140(param_1);
  if (iVar1 == 0) {
    return 0;
  }
  CStaticShadows__UpdateVisibility(param_1,1);
  return 1;
}

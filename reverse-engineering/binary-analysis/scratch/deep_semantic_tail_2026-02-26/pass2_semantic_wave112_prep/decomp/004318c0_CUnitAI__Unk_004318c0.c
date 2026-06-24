/* address: 0x004318c0 */
/* name: CUnitAI__Unk_004318c0 */
/* signature: int __fastcall CUnitAI__Unk_004318c0(int param_1) */


int __fastcall CUnitAI__Unk_004318c0(int param_1)

{
  int iVar1;
  int iVar2;

  iVar1 = (**(code **)(**(int **)(param_1 + 4) + 8))();
  if (*(int *)(param_1 + 8) != 0) {
    iVar2 = CUnitAI__Unk_004318c0(*(int *)(param_1 + 8));
    return iVar1 + 0xc + iVar2;
  }
  return iVar1 + 0xc;
}

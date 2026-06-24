/* address: 0x0042f280 */
/* name: CUnitAI__Unk_0042f280 */
/* signature: int __fastcall CUnitAI__Unk_0042f280(int param_1) */


int __fastcall CUnitAI__Unk_0042f280(int param_1)

{
  int iVar1;
  int iVar2;

  iVar2 = 8;
  if (*(int **)(param_1 + 4) != (int *)0x0) {
    iVar2 = (**(code **)(**(int **)(param_1 + 4) + 8))();
    iVar2 = iVar2 + 8;
  }
  if (*(int *)(param_1 + 8) != 0) {
    iVar1 = CUnitAI__Unk_0042f280(*(int *)(param_1 + 8));
    iVar2 = iVar2 + iVar1;
  }
  return iVar2;
}

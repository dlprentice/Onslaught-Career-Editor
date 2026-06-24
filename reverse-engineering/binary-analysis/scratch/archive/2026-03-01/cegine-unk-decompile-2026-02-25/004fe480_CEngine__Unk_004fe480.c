/* address: 0x004fe480 */
/* name: CEngine__Unk_004fe480 */
/* signature: int __fastcall CEngine__Unk_004fe480(int param_1) */


int __fastcall CEngine__Unk_004fe480(int param_1)

{
  int iVar1;

  if (*(int **)(param_1 + 0x208) != (int *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x004fe48c. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    iVar1 = (**(code **)(**(int **)(param_1 + 0x208) + 0x24))();
    return iVar1;
  }
  return 0;
}

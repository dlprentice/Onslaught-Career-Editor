/* address: 0x004306b0 */
/* name: CSpawnerStatement__Unk_004306b0 */
/* signature: int __fastcall CSpawnerStatement__Unk_004306b0(int param_1) */


int __fastcall CSpawnerStatement__Unk_004306b0(int param_1)

{
  int iVar1;
  int iVar2;

  iVar1 = (**(code **)(**(int **)(param_1 + 4) + 8))();
  if (*(int *)(param_1 + 8) != 0) {
    iVar2 = CSpawnerStatement__Unk_004306b0(*(int *)(param_1 + 8));
    return iVar1 + 0xc + iVar2;
  }
  return iVar1 + 0xc;
}

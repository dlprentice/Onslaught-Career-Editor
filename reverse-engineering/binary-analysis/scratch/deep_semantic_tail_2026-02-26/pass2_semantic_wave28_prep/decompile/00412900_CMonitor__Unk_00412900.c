/* address: 0x00412900 */
/* name: CMonitor__Unk_00412900 */
/* signature: int __fastcall CMonitor__Unk_00412900(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CMonitor__Unk_00412900(int param_1)

{
  int iVar1;
  float *pfVar2;
  undefined1 auStack_10 [16];

  iVar1 = (**(code **)(**(int **)(param_1 + 0x18) + 0x10c))();
  if (iVar1 != 0) {
    pfVar2 = (float *)(**(code **)(**(int **)(param_1 + 0x18) + 0x6c))(auStack_10);
    if (pfVar2[2] * pfVar2[2] + pfVar2[1] * pfVar2[1] + *pfVar2 * *pfVar2 < _DAT_005d8c60) {
      return 0;
    }
  }
  if (*(float *)(*(int *)(param_1 + 0x18) + 0xfc) < _DAT_005d856c) {
    return 0;
  }
  if (_DAT_005d856c < *(float *)(param_1 + 0x48)) {
    return 0;
  }
  return 1;
}

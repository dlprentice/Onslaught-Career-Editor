/* address: 0x00424be0 */
/* name: CUnitAI__Unk_00424be0 */
/* signature: void __fastcall CUnitAI__Unk_00424be0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00424be0(int param_1)

{
  float fVar1;
  void *this;
  int iVar2;
  void *unaff_EDI;
  float10 fVar3;
  undefined **ppuVar4;

  fVar1 = *(float *)(param_1 + 0x120) + *(float *)(param_1 + 0x124);
  *(undefined4 *)(param_1 + 0x128) = *(undefined4 *)(param_1 + 0x124);
  *(float *)(param_1 + 0x124) = fVar1;
  if (fVar1 <= _DAT_005d8568) {
    return;
  }
  if (*(int *)(param_1 + 0x114) == 1) {
    ppuVar4 = (undefined **)&DAT_006235a0;
    this = (void *)(**(code **)(**(int **)(param_1 + 0x8c) + 0x24))();
  }
  else {
    if (*(int *)(param_1 + 0x114) != 2) {
      *(undefined4 *)(param_1 + 0x124) = 0;
      *(undefined4 *)(param_1 + 0x120) = 0;
      return;
    }
    ppuVar4 = &PTR_DAT_0062359c;
    this = (void *)(**(code **)(**(int **)(param_1 + 0x8c) + 0x24))();
  }
  iVar2 = FindAnimationIndex(this,(int)ppuVar4,unaff_EDI);
  *(int *)(param_1 + 0x11c) = iVar2;
  if (*(int **)(param_1 + 0x8c) == (int *)0x0) {
    fVar3 = (float10)_DAT_005d856c;
  }
  else {
    fVar3 = (float10)(**(code **)(**(int **)(param_1 + 0x8c) + 0x38))(iVar2,param_1 + 0x118);
  }
  *(float *)(param_1 + 0x120) = (float)fVar3;
  *(undefined4 *)(param_1 + 0x124) = 0;
  *(undefined4 *)(param_1 + 0x114) = 0;
  return;
}

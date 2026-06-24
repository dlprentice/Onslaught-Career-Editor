/* address: 0x00447a40 */
/* name: CUnitAI__Unk_00447a40 */
/* signature: void __fastcall CUnitAI__Unk_00447a40(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00447a40(int param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;

  if ((*(int *)(param_1 + 0x290) != 0) &&
     ((*(int *)(param_1 + 0x294) != 0 ||
      (iVar3 = CUnitAI__Helper_00447d50((void *)param_1), iVar3 != 0)))) {
    fVar1 = *(float *)(param_1 + 0x114) - _DAT_005d85e8;
    *(undefined4 *)(param_1 + 0x27c) = 2;
    fVar2 = _DAT_005d85e8;
    *(float *)(param_1 + 0x2a0) = fVar1;
    if (fVar2 < fVar1) {
      *(float *)(param_1 + 0x2a0) = fVar1 - _DAT_005d85e0;
      return;
    }
    if (fVar1 < _DAT_005d85dc) {
      *(float *)(param_1 + 0x2a0) = fVar1 + _DAT_005d85e0;
      return;
    }
  }
  return;
}

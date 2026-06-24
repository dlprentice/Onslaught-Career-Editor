/* address: 0x00447b60 */
/* name: CUnitAI__HasReachedCachedAnchorPoint */
/* signature: int __fastcall CUnitAI__HasReachedCachedAnchorPoint(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnitAI__HasReachedCachedAnchorPoint(int param_1)

{
  float fVar1;
  float fVar2;

  if ((*(int *)(param_1 + 0x290) != 0) &&
     (fVar1 = *(float *)(param_1 + 0x1c) - *(float *)(param_1 + 0x280),
     fVar2 = *(float *)(param_1 + 0x20) - *(float *)(param_1 + 0x284),
     SQRT(fVar1 * fVar1 + fVar2 * fVar2) < _DAT_005d85cc)) {
    return 1;
  }
  return 0;
}

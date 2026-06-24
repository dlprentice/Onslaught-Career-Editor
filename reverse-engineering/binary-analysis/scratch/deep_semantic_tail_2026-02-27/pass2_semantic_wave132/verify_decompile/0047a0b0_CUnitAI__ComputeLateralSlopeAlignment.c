/* address: 0x0047a0b0 */
/* name: CUnitAI__ComputeLateralSlopeAlignment */
/* signature: double __fastcall CUnitAI__ComputeLateralSlopeAlignment(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnitAI__ComputeLateralSlopeAlignment(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float10 fVar4;
  float10 fVar5;
  float local_10;
  float local_c;
  float local_8;

  fVar4 = (float10)fcos((float10)*(float *)(param_1 + 0x114));
  local_10 = (float)fVar4;
  fVar5 = (float10)fsin((float10)*(float *)(param_1 + 0x114));
  fVar1 = (float)-fVar5;
  local_c = fVar1;
  CMonitor__Helper_0047ec60(0x6fadc8,&local_10,(void *)(param_1 + 0x1c));
  fVar2 = local_8 * (float)fVar4;
  fVar3 = local_c * fVar1 - (float)fVar4 * local_10;
  fVar1 = SQRT(-(local_8 * fVar1) * -(local_8 * fVar1) + fVar3 * fVar3 + fVar2 * fVar2);
  if (fVar1 != _DAT_005d856c) {
    return (double)((_DAT_005d8568 / fVar1) * fVar3);
  }
  return (double)fVar3;
}

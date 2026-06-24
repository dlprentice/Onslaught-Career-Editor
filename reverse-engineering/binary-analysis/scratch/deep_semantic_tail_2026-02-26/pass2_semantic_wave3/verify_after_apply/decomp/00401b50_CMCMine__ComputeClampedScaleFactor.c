/* address: 0x00401b50 */
/* name: CMCMine__ComputeClampedScaleFactor */
/* signature: double __fastcall CMCMine__ComputeClampedScaleFactor(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CMCMine__ComputeClampedScaleFactor(void *param_1)

{
  float fVar1;
  float10 fVar2;

  fVar2 = (float10)(**(code **)(*(int *)param_1 + 0x60))();
  if (fVar2 <= (float10)_DAT_005d8568) {
    fVar2 = (float10)DAT_008a9e44;
  }
  else {
    fVar1 = DAT_00672fd0 - *(float *)((int)param_1 + 0xd8);
    fVar2 = (float10)(**(code **)(*(int *)param_1 + 0x60))();
    fVar2 = ((float10)_DAT_005d8568 / fVar2) * (float10)fVar1 * (float10)_DAT_005d857c +
            (float10)DAT_008a9e44 * ((float10)_DAT_005d8568 / fVar2);
    if (fVar2 < (float10)_DAT_005d856c) {
      return (double)_DAT_005d856c;
    }
    if ((float10)_DAT_005d8568 < fVar2) {
      return (double)_DAT_005d8568;
    }
  }
  return (double)fVar2;
}

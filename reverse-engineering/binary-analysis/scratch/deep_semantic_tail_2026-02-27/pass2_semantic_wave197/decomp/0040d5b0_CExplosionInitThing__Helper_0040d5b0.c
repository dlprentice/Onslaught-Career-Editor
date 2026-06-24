/* address: 0x0040d5b0 */
/* name: CExplosionInitThing__Helper_0040d5b0 */
/* signature: double __fastcall CExplosionInitThing__Helper_0040d5b0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CExplosionInitThing__Helper_0040d5b0(int param_1)

{
  float fVar1;

  fVar1 = ((DAT_008a9e44 * _DAT_005d8578 + DAT_00672fd0) - *(float *)(param_1 + 4)) /
          (*(float *)(param_1 + 8) - *(float *)(param_1 + 4));
  if (_DAT_005d8568 < fVar1) {
    fVar1 = _DAT_005d8568;
  }
  return (double)fVar1;
}

/* address: 0x004cac40 */
/* name: Math__InvLerpClamp01 */
/* signature: double __cdecl Math__InvLerpClamp01(float param_1, float param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl Math__InvLerpClamp01(float param_1,float param_2,float param_3)

{
  float fVar1;

  fVar1 = (param_1 - param_2) / (param_3 - param_2);
  if (fVar1 < _DAT_005d856c) {
    return (double)_DAT_005d856c;
  }
  if (_DAT_005d8568 < fVar1) {
    fVar1 = _DAT_005d8568;
  }
  return (double)fVar1;
}

/* address: 0x00479630 */
/* name: CMeshCollisionVolume__Helper_00479630 */
/* signature: double __cdecl CMeshCollisionVolume__Helper_00479630(void * param_1, void * param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl CMeshCollisionVolume__Helper_00479630(void *param_1,void *param_2,float param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;

  fVar3 = *(float *)param_2 - *(float *)param_1;
  fVar5 = *(float *)((int)param_2 + 4) - *(float *)((int)param_1 + 4);
  fVar4 = *(float *)((int)param_2 + 8) - *(float *)((int)param_1 + 8);
  fVar1 = SQRT(fVar3 * fVar3 + fVar4 * fVar4 + fVar5 * fVar5);
  if (fVar1 != _DAT_005d856c) {
    fVar1 = _DAT_005d8568 / fVar1;
    fVar3 = fVar3 * fVar1;
    fVar5 = fVar5 * fVar1;
    fVar4 = fVar4 * fVar1;
  }
  fVar1 = -*(float *)param_1;
  fVar2 = -*(float *)((int)param_1 + 4);
  fVar6 = -*(float *)((int)param_1 + 8);
  fVar3 = fVar1 * fVar3 + fVar2 * fVar5 + fVar6 * fVar4;
  fVar4 = param_3 * param_3 - ((fVar1 * fVar1 + fVar2 * fVar2 + fVar6 * fVar6) - fVar3 * fVar3);
  fVar1 = _DAT_005d8be0;
  if (_DAT_005d856c <= fVar4) {
    fVar4 = SQRT(fVar4);
    fVar1 = fVar3 - fVar4;
    if ((fVar1 < _DAT_005d856c) && (fVar1 = _DAT_005d8be0, _DAT_005d856c < fVar4 + fVar3)) {
      return (double)(param_3 -
                     SQRT(*(float *)param_1 * *(float *)param_1 +
                          *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) +
                          *(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8)));
    }
  }
  return (double)fVar1;
}

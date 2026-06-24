/* address: 0x004c7900 */
/* name: CRocket__NormalizeVec3InPlace */
/* signature: void __fastcall CRocket__NormalizeVec3InPlace(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CRocket__NormalizeVec3InPlace(void *param_1)

{
  float fVar1;

  fVar1 = *(float *)((int)param_1 + 8) * *(float *)((int)param_1 + 8) +
          *(float *)((int)param_1 + 4) * *(float *)((int)param_1 + 4) +
          *(float *)param_1 * *(float *)param_1;
  if (_DAT_005d856c < fVar1) {
    fVar1 = _DAT_005d8568 / SQRT(fVar1);
    *(float *)param_1 = fVar1 * *(float *)param_1;
    *(float *)((int)param_1 + 4) = fVar1 * *(float *)((int)param_1 + 4);
    *(float *)((int)param_1 + 8) = fVar1 * *(float *)((int)param_1 + 8);
    return;
  }
  return;
}

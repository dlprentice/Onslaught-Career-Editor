/* address: 0x0040c3c0 */
/* name: CExplosionInitThing__GetCurrentEntrySlotFillRatioOrRacerSpeed */
/* signature: double __fastcall CExplosionInitThing__GetCurrentEntrySlotFillRatioOrRacerSpeed(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CExplosionInitThing__GetCurrentEntrySlotFillRatioOrRacerSpeed(void *param_1)

{
  float fVar1;
  int iVar2;
  float *pfVar3;
  double dVar4;
  undefined1 local_10 [16];

  iVar2 = stricmp(*(char **)(*(int *)((int)param_1 + 0x4b0) + 0xa8),s_Racer_006234f4);
  if (iVar2 == 0) {
    pfVar3 = (float *)(**(code **)(*(int *)param_1 + 0x6c))(local_10);
    fVar1 = SQRT(pfVar3[2] * pfVar3[2] + pfVar3[1] * pfVar3[1] + *pfVar3 * *pfVar3) * _DAT_005d8c64;
    if (_DAT_005d8568 < fVar1) {
      return (double)_DAT_005d8568;
    }
  }
  else {
    if (*(int *)((int)param_1 + 0x260) != 3) {
      dVar4 = CGeneralVolume__GetCurrentEntrySlotFillRatio(*(void **)((int)param_1 + 0x578));
      return dVar4;
    }
    dVar4 = CGeneralVolume__EntryIterator_GetSlotFillRatio(*(void **)((int)param_1 + 0x57c));
    fVar1 = (float)dVar4;
  }
  return (double)fVar1;
}

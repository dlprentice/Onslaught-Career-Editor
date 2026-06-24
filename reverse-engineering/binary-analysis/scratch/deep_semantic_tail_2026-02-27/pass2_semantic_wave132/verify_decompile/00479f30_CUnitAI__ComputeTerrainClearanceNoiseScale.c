/* address: 0x00479f30 */
/* name: CUnitAI__ComputeTerrainClearanceNoiseScale */
/* signature: double __fastcall CUnitAI__ComputeTerrainClearanceNoiseScale(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CUnitAI__ComputeTerrainClearanceNoiseScale(void *param_1)

{
  float10 fVar1;
  float10 extraout_ST0;
  double dVar2;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  float fStack_30;
  float fStack_2c;
  float fStack_28;
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_10;
  float fStack_c;

  if (*(int *)((int)param_1 + 0x274) == 1) {
    return (double)_DAT_005d8df4;
  }
  if (*(int *)((int)param_1 + 0x244) == 2) {
    return (double)_DAT_005d9440;
  }
  if (*(float *)((int)param_1 + 0x84) * *(float *)((int)param_1 + 0x84) +
      *(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
      *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c) <= _DAT_005d856c) {
    return (double)_DAT_005d856c;
  }
  fVar1 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
  fVar1 = fVar1 * (float10)_DAT_005dbce4;
  fStack_10 = (float)(fVar1 * (float10)*(float *)((int)param_1 + 0x40));
  fStack_c = (float)(fVar1 * (float10)*(float *)((int)param_1 + 0x50));
  fStack_40 = fStack_10 + *(float *)((int)param_1 + 0x1c);
  fStack_3c = fStack_c + *(float *)((int)param_1 + 0x20);
  fStack_38 = (float)(fVar1 * (float10)*(float *)((int)param_1 + 0x60) +
                     (float10)*(float *)((int)param_1 + 0x24));
  fVar1 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
  fStack_10 = (float)(-fVar1 * (float10)*(float *)((int)param_1 + 0x40));
  fStack_c = (float)(-fVar1 * (float10)*(float *)((int)param_1 + 0x50));
  Vec3__SetXYZ();
  dVar2 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_40);
  fStack_38 = (float)dVar2;
  dVar2 = CStaticShadows__Helper_0047eb80(0x6fadc8,&fStack_30);
  fStack_28 = (float)dVar2;
  fStack_20 = fStack_40 - fStack_30;
  fStack_1c = fStack_3c - fStack_2c;
  fStack_18 = fStack_38 - fStack_28;
  dVar2 = SQRT__Wrapper_004026b0(&fStack_20);
  if ((double)_DAT_005d856c < dVar2) {
    OID__Helper_0055dcb0();
    return (double)(extraout_ST0 * (float10)_DAT_005db4c8);
  }
  return (double)(_DAT_005d856c * _DAT_005db4c8);
}

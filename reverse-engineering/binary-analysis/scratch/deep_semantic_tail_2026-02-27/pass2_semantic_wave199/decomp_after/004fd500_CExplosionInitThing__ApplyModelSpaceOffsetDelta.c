/* address: 0x004fd500 */
/* name: CExplosionInitThing__ApplyModelSpaceOffsetDelta */
/* signature: void __thiscall CExplosionInitThing__ApplyModelSpaceOffsetDelta(void * this, void * param_1, void * param_2) */


void __thiscall
CExplosionInitThing__ApplyModelSpaceOffsetDelta(void *this,void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float *pfVar5;
  float *extraout_EAX;
  undefined1 *puVar6;
  undefined1 auStack_24 [12];
  undefined1 auStack_18 [24];

  (**(code **)(*(int *)this + 0x168))(param_1);
  puVar6 = auStack_24;
  pfVar5 = (float *)(**(code **)(*(int *)this + 0x78))();
  VFuncSlot_00_00401be0((void *)((int)this + 8),(int)auStack_18,puVar6);
  fVar1 = extraout_EAX[1];
  fVar2 = pfVar5[1];
  fVar3 = extraout_EAX[2];
  fVar4 = pfVar5[2];
  *(float *)param_1 = (*extraout_EAX - *pfVar5) + *(float *)param_1;
  *(float *)((int)param_1 + 4) = (fVar1 - fVar2) + *(float *)((int)param_1 + 4);
  *(float *)((int)param_1 + 8) = (fVar3 - fVar4) + *(float *)((int)param_1 + 8);
  return;
}

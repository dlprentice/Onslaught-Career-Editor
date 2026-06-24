/* address: 0x0040d660 */
/* name: CExplosionInitThing__InterpolateWrappedEulerFromHistory */
/* signature: void __thiscall CExplosionInitThing__InterpolateWrappedEulerFromHistory(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CExplosionInitThing__InterpolateWrappedEulerFromHistory(void *this,int param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;

  fVar1 = *(float *)((int)this + 0x114);
  fVar2 = *(float *)((int)this + 0x590);
  if ((_DAT_005d85c8 <= fVar1) || (fVar2 <= _DAT_005d85e4)) {
    if ((_DAT_005d85e4 < fVar1) && (fVar2 < _DAT_005d85c8)) {
      fVar2 = fVar2 + _DAT_005d85e0;
    }
  }
  else {
    fVar2 = fVar2 - _DAT_005d85e0;
  }
  fVar3 = *(float *)((int)this + 0x118);
  fVar4 = *(float *)((int)this + 0x594);
  if ((_DAT_005d85c8 <= fVar3) || (fVar4 <= _DAT_005d85e4)) {
    if ((_DAT_005d85e4 < fVar3) && (fVar4 < _DAT_005d85c8)) {
      fVar4 = fVar4 + _DAT_005d85e0;
    }
  }
  else {
    fVar4 = fVar4 - _DAT_005d85e0;
  }
  fVar6 = (fVar3 - fVar4) * DAT_008a9e44;
  fVar3 = *(float *)((int)this + 0x594);
  fVar4 = *(float *)((int)this + 0x11c);
  fVar5 = *(float *)((int)this + 0x598);
  if ((_DAT_005d85c8 <= fVar4) || (fVar5 <= _DAT_005d85e4)) {
    if ((_DAT_005d85e4 < fVar4) && (fVar5 < _DAT_005d85c8)) {
      fVar5 = fVar5 + _DAT_005d85e0;
    }
  }
  else {
    fVar5 = fVar5 - _DAT_005d85e0;
  }
  fVar5 = (fVar4 - fVar5) * DAT_008a9e44;
  fVar4 = *(float *)((int)this + 0x598);
  *(float *)param_1 = (fVar1 - fVar2) * DAT_008a9e44 + *(float *)((int)this + 0x590);
  *(float *)(param_1 + 4) = fVar6 + fVar3;
  *(float *)(param_1 + 8) = fVar5 + fVar4;
  return;
}

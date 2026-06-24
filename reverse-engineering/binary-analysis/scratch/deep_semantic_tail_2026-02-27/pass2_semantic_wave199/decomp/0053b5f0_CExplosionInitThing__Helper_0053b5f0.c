/* address: 0x0053b5f0 */
/* name: CExplosionInitThing__Helper_0053b5f0 */
/* signature: void __thiscall CExplosionInitThing__Helper_0053b5f0(void * this, int param_1, float param_2, float param_3, uint param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CExplosionInitThing__Helper_0053b5f0
          (void *this,int param_1,float param_2,float param_3,uint param_4)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  float10 fVar9;
  double dVar10;
  undefined4 local_8;

  if (*(int *)(DAT_008a9d84 + 8) == 0) {
    if ((*(int *)((int)this + 0x5c) == 0) && (*(int *)((int)this + 0x78) != 0)) {
      CVBuffer__LockRange(0,0,(int)this + 0x7c,0x2800);
      *(undefined4 *)((int)this + 0x60) = 0;
      *(undefined4 *)((int)this + 0x5c) = 1;
      fVar1 = DAT_00672fd0;
      dVar10 = CDXEngine__Helper_0055dfe7((double)DAT_00672fd0);
      fVar9 = (float10)fcos(((float10)fVar1 - (float10)dVar10) * (float10)_DAT_005d85e0);
      local_8 = (undefined4)
                (longlong)ROUND((fVar9 + (float10)_DAT_005d8568) * (float10)_DAT_005d963c);
      *(undefined4 *)((int)this + 0x58) = local_8;
    }
    if (*(int *)((int)this + 0x60) != 500) {
      iVar5 = *(int *)((int)this + 0x58);
      iVar8 = iVar5 * 0x10000 + ((uint)param_3 & 0xff0000);
      if (0xff0000 < iVar8) {
        iVar8 = 0xff0000;
      }
      iVar7 = ((uint)param_3 & 0xff00) + iVar5 * 0x100;
      if (0xff00 < iVar7) {
        iVar7 = 0xff00;
      }
      iVar5 = ((uint)param_3 & 0xff) + iVar5;
      if (0xff < iVar5) {
        iVar5 = 0xff;
      }
      RenderState_Set(0x9d,0);
      iVar6 = CExplosionInitThing__CheckValueRange_852_899(0x8a9a98);
      if (iVar6 == 0) {
        fVar1 = (_DAT_008aa4ec + _DAT_008aa4f4) - _DAT_0067a62c;
      }
      else {
        iVar6 = PLATFORM__GetWindowHeight();
        fVar1 = (float)iVar6 * _DAT_005d85ec + _DAT_005e4f94;
      }
      fVar2 = ((float)param_1 * *(float *)((int)this + 0x48) + *(float *)((int)this + 0x50)) -
              _DAT_005dbe74;
      fVar4 = (param_2 * *(float *)((int)this + 0x4c) + *(float *)((int)this + 0x54)) -
              _DAT_005dbe74;
      fVar3 = _DAT_005dbe74 / SQRT(fVar2 * fVar2 + fVar4 * fVar4);
      if (fVar3 < _DAT_005d8568) {
        fVar2 = fVar3 * fVar2;
        fVar4 = fVar3 * fVar4;
      }
      fVar4 = fVar4 + _DAT_005dbe74;
      **(float **)((int)this + 0x7c) =
           (((_DAT_008aa4e8 + _DAT_008aa4f0) - _DAT_005d95b8) - _DAT_0067a628) +
           fVar2 + _DAT_005dbe74 + _DAT_005db4e8;
      *(float *)(*(int *)((int)this + 0x7c) + 4) = (fVar1 - _DAT_005dbe00) - fVar4;
      *(undefined4 *)(*(int *)((int)this + 0x7c) + 8) = 0x3bc49ba6;
      *(undefined4 *)(*(int *)((int)this + 0x7c) + 0xc) = 0x3f000000;
      *(int *)(*(int *)((int)this + 0x7c) + 0x10) = iVar5 + iVar7 + iVar8;
      *(int *)((int)this + 0x7c) = *(int *)((int)this + 0x7c) + 0x14;
      *(int *)((int)this + 0x60) = *(int *)((int)this + 0x60) + 1;
    }
  }
  return;
}

/* address: 0x00413360 */
/* name: CGeneralVolume__Unk_00413360 */
/* signature: void __thiscall CGeneralVolume__Unk_00413360(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Unk_00413360(void *this,int param_1,float param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  float10 fVar7;
  float10 fVar8;
  float10 fVar9;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  float fStack_30;
  float fStack_2c;
  float fStack_28;
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_8;

  iVar6 = (**(code **)(**(int **)((int)this + 0x20) + 0x10c))();
  if ((iVar6 != 0) && (iVar6 = *(int *)((int)this + 0x44), iVar6 < 1)) {
    fVar5 = *(float *)(*(int *)(*(int *)((int)this + 0x20) + 0x4b0) + 0x10) * _DAT_005d8cc8 *
            (float)param_1;
    if ((*(float *)((int)this + 0x3c) < _DAT_006236b0) &&
       ((_DAT_006236b0 < (float)param_1 && (iVar6 == 0)))) {
      *(float *)((int)this + 0x2c) = DAT_00672fd0;
    }
    if ((((*(float *)((int)this + 0x3c) < _DAT_006236b4) && (_DAT_006236b4 < (float)param_1)) &&
        (iVar6 == 0)) &&
       ((DAT_00672fd0 - _DAT_006236ac < *(float *)((int)this + 0x30) &&
        (*(float *)((int)this + 0x30) < DAT_00672fd0 - _DAT_006236ac * _DAT_005d85ec)))) {
      CConsole__Printf(&DAT_0066f580,s_do_dash_RIGHT_00623944);
      CMonitor__Helper_004e1940
                (&DAT_00896988,*(void **)((int)*(void **)((int)this + 0x20) + 0x5b4),
                 *(void **)((int)this + 0x20));
      iVar6 = CGeneralVolume__Unk_00414030(this);
      if (iVar6 != 0) {
        *(undefined4 *)(iVar6 + 0x60) = 0;
      }
      *(undefined4 *)(*(int *)((int)this + 0x20) + 0x2ec) = 0;
      fVar5 = _DAT_006236c0 * fVar5;
      *(float *)(*(int *)((int)this + 0x20) + 0x27c) =
           *(float *)(*(int *)((int)this + 0x20) + 0x27c) - _DAT_005d8ccc;
      *(undefined4 *)((int)this + 0x44) = DAT_006236b8;
    }
    *(int *)((int)this + 0x3c) = param_1;
    fVar7 = (float10)(float)(*(int **)((int)this + 0x20))[0x45];
    fVar8 = (float10)fcos(fVar7);
    fVar1 = (float)fVar8;
    fVar7 = (float10)fsin(fVar7);
    fVar8 = (float10)fcos((float10)_DAT_005d87b0);
    fStack_8 = (float)fVar8;
    fVar9 = (float10)fsin((float10)_DAT_005d87b0);
    fVar2 = (float)fVar9;
    fVar3 = (float)fVar8;
    fVar4 = (float)((float10)(float)fVar9 * (float10)fVar2);
    fStack_30 = (float)((float10)fStack_8 * (float10)fVar1 - (float10)fVar4 * fVar7);
    fStack_2c = (float)-((float10)fVar3 * fVar7);
    fVar8 = (float10)(float)fVar9 * (float10)fStack_8;
    fStack_28 = (float)((float10)fVar2 * (float10)fVar1 + fVar8 * fVar7);
    fStack_20 = (float)((float10)fStack_8 * fVar7 + (float10)fVar4 * (float10)fVar1);
    fStack_1c = fVar3 * fVar1;
    fStack_18 = (float)((float10)fVar2 * fVar7 - fVar8 * (float10)fVar1);
    fStack_8 = fVar3 * fStack_8;
    fStack_40 = fStack_30 * fVar5;
    fStack_3c = fStack_20 * fVar5;
    fStack_38 = -(fVar3 * fVar2) * fVar5;
    (**(code **)(**(int **)((int)this + 0x20) + 0x74))(&fStack_40);
  }
  return;
}

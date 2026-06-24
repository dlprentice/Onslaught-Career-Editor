/* address: 0x00410740 */
/* name: CGeneralVolume__HandleAxisPositiveThresholdCross */
/* signature: void __thiscall CGeneralVolume__HandleAxisPositiveThresholdCross(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CGeneralVolume__HandleAxisPositiveThresholdCross(void *this,int param_1,float param_2)

{
  int *piVar1;
  float *pfVar2;
  float unaff_ESI;
  float local_40;
  float fStack_3c;
  float fStack_38;
  float afStack_30 [4];
  float fStack_20;
  float fStack_10;

  if (*(float *)((int)this + 0x48) == _DAT_005d856c) {
    if (*(int *)((int)this + 0x2c) == 0) {
      if ((_DAT_005d8bb4 < *(float *)((int)this + 0x28)) && ((float)param_1 < _DAT_005d8bb4)) {
        *(float *)((int)this + 0x3c) = DAT_00672fd0;
      }
      if ((((_DAT_005d8be4 < *(float *)((int)this + 0x28)) && ((float)param_1 < _DAT_005d8be4)) &&
          (DAT_00672fd0 - _DAT_005d8604 < *(float *)((int)this + 0x40))) &&
         (*(float *)((int)this + 0x40) < DAT_00672fd0 - _DAT_005d85c0)) {
        piVar1 = *(int **)((int)this + 0x18);
        if ((float)piVar1[0x3f] <= _DAT_005d856c) {
          piVar1[0xb9] = (int)DAT_00672fd0;
        }
        else {
          pfVar2 = (float *)(**(code **)(*piVar1 + 0x6c))(&local_40);
          if (_DAT_005d8c88 < pfVar2[2] * pfVar2[2] + pfVar2[1] * pfVar2[1] + *pfVar2 * *pfVar2) {
            *(undefined4 *)((int)this + 0x48) = 0x41d00000;
            CSquadNormal__Helper_004062d0
                      (afStack_30,*(void **)(*(int *)((int)this + 0x18) + 0x114),0.0,0.0,unaff_ESI);
            local_40 = afStack_30[0] * _DAT_005d8bf0;
            fStack_3c = fStack_20 * _DAT_005d8bf0;
            fStack_38 = fStack_10 * _DAT_005d8bf0;
            (**(code **)(**(int **)((int)this + 0x18) + 0x74))(&local_40);
            *(undefined4 *)((int)this + 0x4c) = 1;
          }
        }
      }
      piVar1 = *(int **)((int)this + 0x18);
      *(int *)((int)this + 0x28) = param_1;
      if (((float)piVar1[0x3f] != _DAT_005d856c) && (_DAT_005d85ec < ABS((float)param_1))) {
        local_40 = (float)param_1 * _DAT_005d8c98;
        fStack_38 = local_40 * (float)piVar1[0x17];
        fStack_3c = local_40 * (float)piVar1[0x13];
        local_40 = local_40 * (float)piVar1[0xf];
        (**(code **)(*piVar1 + 0x74))(&local_40);
        *(float *)((int)this + 0x50) = DAT_00672fd0;
        return;
      }
    }
    else if (*(int *)((int)this + 0x34) == 0) {
      if ((_DAT_005d8bb4 < *(float *)((int)this + 0x28)) && ((float)param_1 < _DAT_005d8bb4)) {
        *(float *)((int)this + 0x3c) = DAT_00672fd0;
      }
      if (((_DAT_005d85f8 < (float)param_1) &&
          (DAT_00672fd0 - _DAT_005d8604 < *(float *)((int)this + 0x40))) &&
         (*(float *)((int)this + 0x40) < DAT_00672fd0 - _DAT_005d85c0)) {
        *(undefined4 *)((int)this + 0x34) = 1;
        return;
      }
    }
  }
  return;
}

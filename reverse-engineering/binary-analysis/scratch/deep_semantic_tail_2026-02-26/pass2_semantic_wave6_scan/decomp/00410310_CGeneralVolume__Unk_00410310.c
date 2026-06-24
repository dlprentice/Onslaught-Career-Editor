/* address: 0x00410310 */
/* name: CGeneralVolume__Unk_00410310 */
/* signature: void __thiscall CGeneralVolume__Unk_00410310(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Unk_00410310(void *this,int param_1,float param_2)

{
  int *piVar1;
  float *pfVar2;
  undefined1 local_10 [16];

  if (*(float *)((int)this + 0x48) <= _DAT_005d856c) {
    if ((*(int *)((int)this + 0x2c) == 0) &&
       (piVar1 = *(int **)((int)this + 0x18), (float)piVar1[0x3f] != _DAT_005d856c)) {
      *(float *)((int)this + 0x20) = _DAT_005d85ec - (float)param_1 * _DAT_005d85ec;
      if ((_DAT_005d8c8c < *(float *)((int)this + 0x24)) && ((float)param_1 < _DAT_005d8bb4)) {
        *(float *)((int)this + 0x44) = DAT_00672fd0;
      }
      if (((_DAT_005d85f8 < (float)param_1) &&
          (DAT_00672fd0 - _DAT_005d8604 < *(float *)((int)this + 0x44))) &&
         (*(float *)((int)this + 0x44) < DAT_00672fd0 - _DAT_005d85c0)) {
        if ((float)piVar1[0x3f] <= _DAT_005d856c) {
          piVar1[0xb9] = (int)DAT_00672fd0;
          *(int *)((int)this + 0x24) = param_1;
          return;
        }
        pfVar2 = (float *)(**(code **)(*piVar1 + 0x6c))(local_10);
        if (_DAT_005d8c88 < pfVar2[2] * pfVar2[2] + pfVar2[1] * pfVar2[1] + *pfVar2 * *pfVar2) {
          *(undefined4 *)((int)this + 0x2c) = 1;
          *(undefined4 *)((int)this + 0x30) = 0;
          *(undefined4 *)((int)this + 0x34) = 0;
          *(float *)(*(int *)((int)this + 0x18) + 0x280) =
               *(float *)(*(int *)((int)this + 0x18) + 0x280) - _DAT_005d8c2c;
          *(int *)((int)this + 0x24) = param_1;
          return;
        }
      }
    }
    *(int *)((int)this + 0x24) = param_1;
  }
  return;
}

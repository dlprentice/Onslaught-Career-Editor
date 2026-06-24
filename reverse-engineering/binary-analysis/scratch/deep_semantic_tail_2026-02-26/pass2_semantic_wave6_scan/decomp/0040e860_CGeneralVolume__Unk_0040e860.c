/* address: 0x0040e860 */
/* name: CGeneralVolume__Unk_0040e860 */
/* signature: void __thiscall CGeneralVolume__Unk_0040e860(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Unk_0040e860(void *this,void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  int *piVar3;
  float *pfVar4;
  undefined1 local_40 [16];
  undefined1 auStack_30 [48];

  if (*(int **)((int)this + 0x528) != (int *)0x0) {
    piVar3 = (int *)(**(code **)(**(int **)((int)this + 0x528) + 0x10))();
    (**(code **)(*piVar3 + 0x1c))(&PTR_DAT_006234fc,1,param_1,auStack_30,0,1);
  }
  pfVar4 = (float *)(**(code **)(*(int *)this + 0x6c))(local_40);
  fVar1 = pfVar4[1] * _DAT_005d85ec;
  fVar2 = pfVar4[2] * _DAT_005d85ec;
  *(float *)param_1 = *pfVar4 * _DAT_005d85ec + *(float *)param_1;
  *(float *)((int)param_1 + 4) = fVar1 + *(float *)((int)param_1 + 4);
  *(float *)((int)param_1 + 8) = fVar2 + *(float *)((int)param_1 + 8);
  return;
}

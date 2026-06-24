/* address: 0x004e97e0 */
/* name: CUnit__Unk_004e97e0 */
/* signature: int __thiscall CUnit__Unk_004e97e0(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CUnit__Unk_004e97e0(void *this,void *param_1,void *param_2)

{
  int iVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  void *pvVar6;
  void *extraout_EAX;
  void *extraout_EAX_00;
  void *extraout_EAX_01;
  void *extraout_EAX_02;
  void *unaff_EDI;
  undefined1 local_70 [16];
  float local_60;
  float local_5c;
  float local_50;
  float local_4c;
  float local_40;
  float local_3c;
  float local_30;
  float local_2c;
  undefined1 local_20 [16];
  undefined1 local_10 [16];

  iVar1 = *(int *)((int)this + 0x10);
  pvVar6 = (void *)Vec3__SetXYZ();
  CGeneralVolume__Unk_0040d2c0
            ((void *)(*(int *)((int)this + 0x10) + 0x3c),local_10,pvVar6,unaff_EDI);
  Vec3__Add((void *)(iVar1 + 0x1c),local_70,extraout_EAX,unaff_EDI);
  Vec3__SetXYZ();
  iVar1 = *(int *)((int)param_1 + 0x10);
  pvVar6 = (void *)Vec3__SetXYZ();
  CGeneralVolume__Unk_0040d2c0
            ((void *)(*(int *)((int)param_1 + 0x10) + 0x3c),local_20,pvVar6,unaff_EDI);
  Vec3__Add((void *)(iVar1 + 0x1c),local_70,extraout_EAX_00,unaff_EDI);
  Vec3__SetXYZ();
  iVar1 = *(int *)((int)this + 0x10);
  pvVar6 = (void *)Vec3__SetXYZ();
  CGeneralVolume__Unk_0040d2c0
            ((void *)(*(int *)((int)this + 0x10) + 0x3c),local_20,pvVar6,unaff_EDI);
  Vec3__Add((void *)(iVar1 + 0x1c),local_70,extraout_EAX_01,unaff_EDI);
  Vec3__SetXYZ();
  iVar1 = *(int *)((int)param_1 + 0x10);
  pvVar6 = (void *)Vec3__SetXYZ();
  CGeneralVolume__Unk_0040d2c0
            ((void *)(*(int *)((int)param_1 + 0x10) + 0x3c),local_20,pvVar6,unaff_EDI);
  Vec3__Add((void *)(iVar1 + 0x1c),local_70,extraout_EAX_02,unaff_EDI);
  Vec3__SetXYZ();
  fVar2 = SQRT(local_60 * local_60 + local_5c * local_5c) + _DAT_005d8568;
  fVar5 = SQRT(local_50 * local_50 + local_4c * local_4c) + _DAT_005d8568;
  fVar4 = SQRT(local_40 * local_40 + local_3c * local_3c) + _DAT_005d8568;
  fVar3 = SQRT(local_30 * local_30 + local_2c * local_2c) + _DAT_005d8568;
  if (fVar4 * fVar4 + fVar3 * fVar3 < fVar2 * fVar2 + fVar5 * fVar5) {
    pvVar6 = *(void **)this;
    CGenericActiveReader__SetReader(this,*(void **)param_1);
    CGenericActiveReader__SetReader(param_1,pvVar6);
    return 1;
  }
  return 0;
}

/* address: 0x004f8140 */
/* name: CActor__Helper_004f8140 */
/* signature: void __thiscall CActor__Helper_004f8140(void * this, void * param_1, int param_2, int param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CActor__Helper_004f8140(void *this,void *param_1,int param_2,int param_3,int param_4)

{
  undefined4 *puVar1;
  undefined4 *extraout_EAX;
  int iVar2;
  void *unaff_EDI;
  undefined4 *puVar3;
  float10 fVar4;
  float10 fVar5;
  float10 fVar6;
  float10 fVar7;
  undefined4 local_8c;
  float local_84;
  float local_80;
  undefined4 local_7c;
  undefined4 local_74;
  float local_70;
  float local_6c;
  undefined4 local_68;
  undefined4 local_64;
  float local_60;
  float local_5c;
  undefined4 local_58;
  float local_54;
  undefined4 local_30 [12];

  fVar4 = (float10)fcos((float10)param_3 * (float10)_DAT_005dfb6c);
  fVar5 = (float10)fsin((float10)(float)((float10)param_3 * (float10)_DAT_005dfb6c));
  *(float *)this = (float)fVar4;
  *(undefined4 *)((int)this + 4) = 0;
  *(float *)((int)this + 8) = (float)fVar5;
  *(undefined4 *)((int)this + 0xc) = local_8c;
  *(undefined4 *)((int)this + 0x10) = 0;
  *(undefined4 *)((int)this + 0x14) = 0x3f800000;
  fVar7 = (float10)_DAT_005dfb6c;
  *(undefined4 *)((int)this + 0x18) = 0;
  *(undefined4 *)((int)this + 0x1c) = local_8c;
  fVar6 = (float10)fcos((float10)param_2 * fVar7);
  *(float *)((int)this + 0x20) = (float)-fVar5;
  *(undefined4 *)((int)this + 0x24) = 0;
  *(float *)((int)this + 0x28) = (float)fVar4;
  local_80 = 0.0;
  *(undefined4 *)((int)this + 0x2c) = local_8c;
  local_84 = 1.0;
  local_7c = 0;
  local_74 = 0;
  local_70 = (float)fVar6;
  fVar7 = (float10)fsin((float10)(float)((float10)param_2 * fVar7));
  local_6c = (float)-fVar7;
  local_60 = (float)fVar7;
  local_5c = (float)fVar6;
  local_64 = 0;
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Vec3__SetXYZ();
  Mat34__SetRows();
  fVar7 = (float10)_DAT_005dfb6c;
  puVar1 = local_30;
  puVar3 = this;
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar3 = *puVar1;
    puVar1 = puVar1 + 1;
    puVar3 = puVar3 + 1;
  }
  fVar4 = (float10)fcos((float10)(int)param_1 * fVar7);
  local_7c = 0;
  local_54 = (float)fVar4;
  local_84 = (float)fVar4;
  fVar7 = (float10)fsin((float10)(int)param_1 * fVar7);
  local_80 = (float)-fVar7;
  puVar1 = (undefined4 *)Vec3__SetXYZ();
  local_74 = *puVar1;
  local_70 = (float)puVar1[1];
  local_6c = (float)puVar1[2];
  local_68 = puVar1[3];
  puVar1 = (undefined4 *)Vec3__SetXYZ();
  local_64 = *puVar1;
  local_60 = (float)puVar1[1];
  local_5c = (float)puVar1[2];
  local_58 = puVar1[3];
  CMCBuggy__Helper_0040d320(&local_84,local_30,this,unaff_EDI);
  puVar1 = extraout_EAX;
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *(undefined4 *)this = *puVar1;
    puVar1 = puVar1 + 1;
    this = (undefined4 *)((int)this + 4);
  }
  return;
}

/* address: 0x00495ed0 */
/* name: CMCMech__Helper_00495ed0 */
/* signature: void __thiscall CMCMech__Helper_00495ed0(void * this, void * param_1, void * param_2, float param_3) */


void __thiscall CMCMech__Helper_00495ed0(void *this,void *param_1,void *param_2,float param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  undefined4 local_24;
  undefined4 local_14;
  undefined4 local_4;

  fVar1 = *(float *)((int)this + 0x20);
  fVar2 = *(float *)((int)this + 0x24);
  fVar3 = *(float *)((int)this + 0x28);
  fVar4 = *(float *)((int)this + 0x10);
  fVar5 = *(float *)((int)this + 0x14);
  fVar6 = *(float *)((int)this + 0x18);
  fVar7 = *(float *)((int)this + 4);
  fVar8 = *(float *)((int)this + 8);
  *(float *)param_1 = (float)param_2 * *(float *)this;
  *(float *)((int)param_1 + 4) = (float)param_2 * fVar7;
  *(float *)((int)param_1 + 8) = (float)param_2 * fVar8;
  *(undefined4 *)((int)param_1 + 0xc) = local_24;
  *(float *)((int)param_1 + 0x10) = (float)param_2 * fVar4;
  *(float *)((int)param_1 + 0x14) = (float)param_2 * fVar5;
  *(float *)((int)param_1 + 0x18) = (float)param_2 * fVar6;
  *(undefined4 *)((int)param_1 + 0x1c) = local_14;
  *(float *)((int)param_1 + 0x20) = (float)param_2 * fVar1;
  *(float *)((int)param_1 + 0x24) = (float)param_2 * fVar2;
  *(float *)((int)param_1 + 0x28) = (float)param_2 * fVar3;
  *(undefined4 *)((int)param_1 + 0x2c) = local_4;
  return;
}

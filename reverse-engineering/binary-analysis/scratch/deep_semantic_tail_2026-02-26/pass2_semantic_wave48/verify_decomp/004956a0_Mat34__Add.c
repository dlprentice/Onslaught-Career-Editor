/* address: 0x004956a0 */
/* name: Mat34__Add */
/* signature: void __thiscall Mat34__Add(void * this, void * param_1, void * param_2, void * param_3) */


void __thiscall Mat34__Add(void *this,void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  undefined4 local_24;
  undefined4 local_14;
  undefined4 local_4;

  fVar1 = *(float *)((int)this + 0x20);
  fVar2 = *(float *)((int)param_2 + 0x20);
  fVar3 = *(float *)((int)param_2 + 0x24);
  fVar4 = *(float *)((int)this + 0x24);
  fVar5 = *(float *)((int)param_2 + 0x28);
  fVar6 = *(float *)((int)this + 0x28);
  fVar7 = *(float *)((int)param_2 + 0x10);
  fVar8 = *(float *)((int)this + 0x10);
  fVar9 = *(float *)((int)param_2 + 0x14);
  fVar10 = *(float *)((int)this + 0x14);
  fVar11 = *(float *)((int)param_2 + 0x18);
  fVar12 = *(float *)((int)this + 0x18);
  fVar13 = *(float *)((int)param_2 + 4);
  fVar14 = *(float *)((int)this + 4);
  fVar15 = *(float *)((int)param_2 + 8);
  fVar16 = *(float *)((int)this + 8);
  *(float *)param_1 = *(float *)param_2 + *(float *)this;
  *(float *)((int)param_1 + 4) = fVar13 + fVar14;
  *(float *)((int)param_1 + 8) = fVar15 + fVar16;
  *(undefined4 *)((int)param_1 + 0xc) = local_24;
  *(float *)((int)param_1 + 0x10) = fVar7 + fVar8;
  *(float *)((int)param_1 + 0x14) = fVar9 + fVar10;
  *(float *)((int)param_1 + 0x18) = fVar11 + fVar12;
  *(undefined4 *)((int)param_1 + 0x1c) = local_14;
  *(float *)((int)param_1 + 0x20) = fVar1 + fVar2;
  *(float *)((int)param_1 + 0x24) = fVar3 + fVar4;
  *(float *)((int)param_1 + 0x28) = fVar5 + fVar6;
  *(undefined4 *)((int)param_1 + 0x2c) = local_4;
  return;
}

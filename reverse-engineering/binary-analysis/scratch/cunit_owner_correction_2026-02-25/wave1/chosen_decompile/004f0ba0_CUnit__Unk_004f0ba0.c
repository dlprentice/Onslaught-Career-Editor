/* address: 0x004f0ba0 */
/* name: CUnit__Unk_004f0ba0 */
/* signature: void __thiscall CUnit__Unk_004f0ba0(void * this, int param_1, void * param_2) */


void __thiscall CUnit__Unk_004f0ba0(void *this,int param_1,void *param_2)

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
  undefined4 local_14;

  fVar1 = *(float *)((int)this + 0x4c);
  fVar2 = *(float *)((int)this + 0x2d4);
  fVar3 = *(float *)((int)this + 0x54);
  fVar4 = *(float *)((int)this + 0x2dc);
  fVar5 = *(float *)((int)this + 0x50);
  fVar6 = *(float *)((int)this + 0x2d8);
  fVar7 = *(float *)((int)this + 0x5c);
  fVar8 = *(float *)((int)this + 0x2d4);
  fVar9 = *(float *)((int)this + 100);
  fVar10 = *(float *)((int)this + 0x2dc);
  fVar11 = *(float *)((int)this + 0x60);
  fVar12 = *(float *)((int)this + 0x2d8);
  fVar13 = *(float *)((int)this + 0x20);
  fVar14 = *(float *)((int)this + 0x24);
  *(float *)param_1 =
       *(float *)((int)this + 0x2d4) * *(float *)((int)this + 0x3c) +
       *(float *)((int)this + 0x40) * *(float *)((int)this + 0x2d8) +
       *(float *)((int)this + 0x44) * *(float *)((int)this + 0x2dc) + *(float *)((int)this + 0x1c);
  *(float *)(param_1 + 4) = fVar5 * fVar6 + fVar3 * fVar4 + fVar1 * fVar2 + fVar13;
  *(float *)(param_1 + 8) = fVar11 * fVar12 + fVar9 * fVar10 + fVar7 * fVar8 + fVar14;
  *(undefined4 *)(param_1 + 0xc) = local_14;
  return;
}

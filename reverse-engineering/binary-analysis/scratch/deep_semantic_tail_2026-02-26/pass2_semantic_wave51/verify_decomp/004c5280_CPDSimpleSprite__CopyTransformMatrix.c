/* address: 0x004c5280 */
/* name: CPDSimpleSprite__CopyTransformMatrix */
/* signature: void __thiscall CPDSimpleSprite__CopyTransformMatrix(void * this, void * param_1, void * param_2) */


void __thiscall CPDSimpleSprite__CopyTransformMatrix(void *this,void *param_1,void *param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 local_24;
  undefined4 local_14;
  undefined4 local_4;

  uVar1 = *(undefined4 *)((int)this + 8);
  uVar2 = *(undefined4 *)((int)this + 0x18);
  uVar3 = *(undefined4 *)((int)this + 0x28);
  uVar4 = *(undefined4 *)((int)this + 4);
  uVar5 = *(undefined4 *)((int)this + 0x14);
  uVar6 = *(undefined4 *)((int)this + 0x24);
  uVar7 = *(undefined4 *)((int)this + 0x10);
  uVar8 = *(undefined4 *)((int)this + 0x20);
  *(undefined4 *)param_1 = *(undefined4 *)this;
  *(undefined4 *)((int)param_1 + 4) = uVar7;
  *(undefined4 *)((int)param_1 + 8) = uVar8;
  *(undefined4 *)((int)param_1 + 0xc) = local_24;
  *(undefined4 *)((int)param_1 + 0x10) = uVar4;
  *(undefined4 *)((int)param_1 + 0x14) = uVar5;
  *(undefined4 *)((int)param_1 + 0x18) = uVar6;
  *(undefined4 *)((int)param_1 + 0x1c) = local_14;
  *(undefined4 *)((int)param_1 + 0x20) = uVar1;
  *(undefined4 *)((int)param_1 + 0x24) = uVar2;
  *(undefined4 *)((int)param_1 + 0x28) = uVar3;
  *(undefined4 *)((int)param_1 + 0x2c) = local_4;
  return;
}

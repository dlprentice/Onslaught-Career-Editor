/* address: 0x00443780 */
/* name: CDestroyableSwapSegment__VFunc_03_00443780 */
/* signature: void __thiscall CDestroyableSwapSegment__VFunc_03_00443780(void * this, void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDestroyableSwapSegment__VFunc_03_00443780(void *this,void *param_1,float param_2)

{
  bool bVar1;
  float fVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;

  iVar4 = (**(code **)(*(int *)this + 0x10))();
  if (*(int *)((int)this + 0x1c) != 0) {
    fVar2 = *(float *)((int)this + 0xc) - (float)param_1;
    *(float *)((int)this + 0xc) = fVar2;
    uVar3 = DAT_00672fd0;
    bVar1 = fVar2 < _DAT_005d856c;
    *(void **)((int)this + 0x18) = param_1;
    *(undefined4 *)((int)this + 0x14) = uVar3;
    if (bVar1) {
      *(undefined4 *)((int)this + 0xc) = 0;
    }
  }
  iVar5 = (**(code **)(*(int *)this + 0x10))();
  if (iVar4 != iVar5) {
    (**(code **)(*(int *)this + 0x28))();
    if (iVar4 == 0) {
      CDestructableSegment__Unk_004429a0(this);
    }
    *(float *)((int)this + 0x34) = *(float *)((int)this + 0x34) * _DAT_005d85ec;
    **(undefined4 **)((int)this + 0x3c) = 1;
  }
  if (*(float *)((int)this + 0xc) == _DAT_005d856c) {
    (**(code **)(*(int *)this + 0x20))();
  }
  return;
}

/* address: 0x0046bab0 */
/* name: CUnitAI__Unk_0046bab0 */
/* signature: void __thiscall CUnitAI__Unk_0046bab0(void * this, int param_1, int param_2) */


void __thiscall CUnitAI__Unk_0046bab0(void *this,int param_1,int param_2)

{
  int iVar1;
  void *this_00;
  int iVar2;
  float10 fVar3;

  this_00 = (void *)(**(code **)(**(int **)((int)this + 0x58) + 0x24))();
  if (this_00 != (void *)0x0) {
    iVar1 = **(int **)((int)this + 0x58);
    iVar2 = FindAnimationIndex(this_00,param_1,(void *)((int)this + 0x44));
    fVar3 = (float10)(**(code **)(iVar1 + 0x38))(iVar2);
    *(float *)((int)this + 0x48) = (float)fVar3;
    *(undefined4 *)((int)this + 0x4c) = 0;
  }
  return;
}

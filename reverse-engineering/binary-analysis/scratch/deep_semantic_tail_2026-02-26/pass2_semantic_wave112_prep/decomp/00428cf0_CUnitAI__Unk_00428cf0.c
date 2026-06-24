/* address: 0x00428cf0 */
/* name: CUnitAI__Unk_00428cf0 */
/* signature: void __thiscall CUnitAI__Unk_00428cf0(void * this, int param_1, int param_2) */


void __thiscall CUnitAI__Unk_00428cf0(void *this,int param_1,int param_2)

{
  float unaff_EDI;

  if ((*(int *)(*(int *)((int)this + 0x164) + 0x134) != 0) &&
     (*(int **)((int)this + 0x26c) != (int *)0x0)) {
    (**(code **)(**(int **)((int)this + 0x26c) + 0x1ac))(param_1);
  }
  CUnitAI__Helper_004fe540(this,(void *)param_1,unaff_EDI);
  return;
}

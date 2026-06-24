/* address: 0x004f4530 */
/* name: CUnit__Unk_004f4530 */
/* signature: int __thiscall CUnit__Unk_004f4530(void * this, int param_1, int param_2) */


int __thiscall CUnit__Unk_004f4530(void *this,int param_1,int param_2)

{
  void *this_00;
  int iVar1;
  void *unaff_retaddr;

  if (*(int **)((int)this + 0x30) == (int *)0x0) {
    return 0;
  }
  this_00 = (void *)(**(code **)(**(int **)((int)this + 0x30) + 0x24))();
  if (this_00 == (void *)0x0) {
    return 0;
  }
  iVar1 = FindAnimationIndex(this_00,param_1,unaff_retaddr);
  return iVar1;
}

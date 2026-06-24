/* address: 0x004f4560 */
/* name: CGillMHead__Helper_004f4560 */
/* signature: void __thiscall CGillMHead__Helper_004f4560(void * this, void * param_1, int param_2, int param_3, int param_4) */


void __thiscall
CGillMHead__Helper_004f4560(void *this,void *param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  void *this_00;
  void *unaff_ESI;

  if (*(int **)((int)this + 0x30) == (int *)0x0) {
    iVar1 = 0;
  }
  else {
    this_00 = (void *)(**(code **)(**(int **)((int)this + 0x30) + 0x24))();
    iVar1 = 0;
    if (this_00 != (void *)0x0) {
      iVar1 = FindAnimationIndex(this_00,(int)param_1,unaff_ESI);
    }
  }
  (**(code **)(*(int *)this + 0xf0))(iVar1,param_2,param_3);
  return;
}

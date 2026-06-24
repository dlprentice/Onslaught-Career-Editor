/* address: 0x004fde70 */
/* name: CWarspite__TransitionToUndeploying */
/* signature: void __thiscall CWarspite__TransitionToUndeploying(void * this) */


void __thiscall CWarspite__TransitionToUndeploying(void *this)

{
  int iVar1;
  void *this_00;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  if (*(int *)((int)this + 0x244) == 4) {
    iVar1 = *(int *)this;
    *(undefined4 *)((int)this + 0x244) = 5;
    pvVar4 = (void *)0x1;
    pcVar3 = s_undeploying_006239d8;
    this_00 = (void *)(**(code **)(**(int **)((int)this + 0x30) + 0x24))(s_undeploying_006239d8,1,0)
    ;
    iVar2 = FindAnimationIndex(this_00,(int)pcVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
  }
  return;
}

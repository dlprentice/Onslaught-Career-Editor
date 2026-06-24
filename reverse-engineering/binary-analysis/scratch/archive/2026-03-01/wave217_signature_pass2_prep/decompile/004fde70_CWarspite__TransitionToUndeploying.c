/* address: 0x004fde70 */
/* name: CWarspite__TransitionToUndeploying */
/* signature: void __fastcall CWarspite__TransitionToUndeploying(void * param_1) */


void __fastcall CWarspite__TransitionToUndeploying(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  if (*(int *)((int)param_1 + 0x244) == 4) {
    iVar1 = *(int *)param_1;
    *(undefined4 *)((int)param_1 + 0x244) = 5;
    pvVar4 = (void *)0x1;
    pcVar3 = s_undeploying_006239d8;
    this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_undeploying_006239d8,1,0)
    ;
    iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
  }
  return;
}

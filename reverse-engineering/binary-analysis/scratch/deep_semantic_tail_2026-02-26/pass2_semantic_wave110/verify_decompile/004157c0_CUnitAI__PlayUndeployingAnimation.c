/* address: 0x004157c0 */
/* name: CUnitAI__PlayUndeployingAnimation */
/* signature: void __fastcall CUnitAI__PlayUndeployingAnimation(void * param_1) */


void __fastcall CUnitAI__PlayUndeployingAnimation(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  iVar1 = *(int *)param_1;
  *(undefined4 *)((int)param_1 + 0x1f0) = 0;
  pvVar4 = (void *)0x1;
  pcVar3 = s_undeploying_006239d8;
  this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_undeploying_006239d8,1,0);
  iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
  (**(code **)(iVar1 + 0xf0))(iVar2);
  return;
}

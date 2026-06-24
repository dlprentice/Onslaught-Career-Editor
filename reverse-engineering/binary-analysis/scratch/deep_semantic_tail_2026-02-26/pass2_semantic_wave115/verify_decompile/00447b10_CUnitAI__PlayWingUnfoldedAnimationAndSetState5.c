/* address: 0x00447b10 */
/* name: CUnitAI__PlayWingUnfoldedAnimationAndSetState5 */
/* signature: void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * param_1) */


void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  iVar1 = *(int *)param_1;
  pvVar4 = (void *)0x1;
  pcVar3 = s_wingunfolded_00628ab0;
  this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_wingunfolded_00628ab0,1,0);
  iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
  (**(code **)(iVar1 + 0xf0))(iVar2);
  *(undefined4 *)((int)param_1 + 0x27c) = 5;
  CWorld__DispatchHelper_004bc3e0(param_1);
  return;
}

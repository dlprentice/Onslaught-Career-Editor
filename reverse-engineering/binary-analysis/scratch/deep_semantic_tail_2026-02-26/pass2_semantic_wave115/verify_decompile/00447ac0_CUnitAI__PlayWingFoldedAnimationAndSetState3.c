/* address: 0x00447ac0 */
/* name: CUnitAI__PlayWingFoldedAnimationAndSetState3 */
/* signature: void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void * param_1) */


void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  *(undefined4 *)((int)param_1 + 0x27c) = 3;
  *(undefined4 *)((int)param_1 + 0x290) = 0;
  CWorld__DispatchHelper_004bc480(param_1);
  iVar1 = *(int *)param_1;
  pvVar4 = (void *)0x1;
  pcVar3 = s_wingfolded_00628aa4;
  this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_wingfolded_00628aa4,1,0);
  iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
  (**(code **)(iVar1 + 0xf0))(iVar2);
  return;
}

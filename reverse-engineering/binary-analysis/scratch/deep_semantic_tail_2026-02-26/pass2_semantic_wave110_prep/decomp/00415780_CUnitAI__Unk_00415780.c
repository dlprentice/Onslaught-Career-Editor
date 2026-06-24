/* address: 0x00415780 */
/* name: CUnitAI__Unk_00415780 */
/* signature: void __fastcall CUnitAI__Unk_00415780(void * param_1) */


void __fastcall CUnitAI__Unk_00415780(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  if (*(int *)((int)param_1 + 0x260) == 0) {
    iVar1 = *(int *)param_1;
    pvVar4 = (void *)0x1;
    pcVar3 = s_deploying_006239cc;
    this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_deploying_006239cc,1,0);
    iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
    *(undefined4 *)((int)param_1 + 0x260) = 1;
  }
  return;
}

/* address: 0x004455c0 */
/* name: CUnitAI__Unk_004455c0 */
/* signature: void __fastcall CUnitAI__Unk_004455c0(void * param_1) */


void __fastcall CUnitAI__Unk_004455c0(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  if ((*(int *)((int)param_1 + 0x280) == 0) || (*(int *)((int)param_1 + 0x280) == 2)) {
    iVar1 = *(int *)param_1;
    *(undefined4 *)((int)param_1 + 0x280) = 3;
    pvVar4 = (void *)0x1;
    pcVar3 = s_close_006289e4;
    this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_close_006289e4,1,0);
    iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
  }
  return;
}

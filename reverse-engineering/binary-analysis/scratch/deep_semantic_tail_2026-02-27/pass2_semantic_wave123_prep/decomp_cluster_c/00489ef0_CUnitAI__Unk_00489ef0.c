/* address: 0x00489ef0 */
/* name: CUnitAI__Unk_00489ef0 */
/* signature: void __fastcall CUnitAI__Unk_00489ef0(void * param_1) */


void __fastcall CUnitAI__Unk_00489ef0(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  char *pcVar3;
  void *pvVar4;

  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    iVar1 = *(int *)param_1;
    pvVar4 = (void *)0x1;
    pcVar3 = s_dead_forward_0062d518;
    this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                             (s_dead_forward_0062d518,1,1);
    iVar2 = FindAnimationIndex(this,(int)pcVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
  }
  *(undefined4 *)((int)param_1 + 0x26c) = 0;
  CUnitAI__Helper_00402000((int)param_1);
  return;
}

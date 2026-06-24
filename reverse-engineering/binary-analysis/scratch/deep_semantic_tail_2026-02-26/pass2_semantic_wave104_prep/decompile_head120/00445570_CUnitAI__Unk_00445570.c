/* address: 0x00445570 */
/* name: CUnitAI__Unk_00445570 */
/* signature: void __fastcall CUnitAI__Unk_00445570(void * param_1) */


void __fastcall CUnitAI__Unk_00445570(void *param_1)

{
  int iVar1;
  void *this;
  int iVar2;
  undefined *puVar3;
  void *pvVar4;

  if ((*(int *)((int)param_1 + 0x280) == 1) || (*(int *)((int)param_1 + 0x280) == 3)) {
    iVar1 = *(int *)param_1;
    *(undefined4 *)((int)param_1 + 0x280) = 2;
    pvVar4 = (void *)0x1;
    puVar3 = &DAT_00623bb4;
    this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(&DAT_00623bb4,1,0);
    iVar2 = FindAnimationIndex(this,(int)puVar3,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar2);
  }
  return;
}

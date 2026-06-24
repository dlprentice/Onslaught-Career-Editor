/* address: 0x00445610 */
/* name: CUnitAI__AdvanceOpenCloseShootAnimationState */
/* signature: int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * param_1) */


int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  void *unaff_EBX;
  char *pcVar4;
  undefined **ppuVar5;
  void *pvVar6;
  undefined *puVar7;

  iVar1 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar1 == -1) {
    return 1;
  }
  puVar7 = &DAT_00623bb4;
  pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(pvVar2,(int)puVar7,unaff_EBX);
  iVar3 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar3 == iVar1) {
    iVar1 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar4 = s_shoot_006289ec;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_shoot_006289ec,1,1);
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar4,pvVar6);
    (**(code **)(iVar1 + 0xf0))(iVar3);
    *(undefined4 *)((int)param_1 + 0x280) = 0;
    return 0;
  }
  pcVar4 = s_close_006289e4;
  pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(pvVar2,(int)pcVar4,unaff_EBX);
  iVar3 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar3 == iVar1) {
    iVar1 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    ppuVar5 = &PTR_DAT_0062359c;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(&PTR_DAT_0062359c,1,1);
    iVar3 = FindAnimationIndex(pvVar2,(int)ppuVar5,pvVar6);
    (**(code **)(iVar1 + 0xf0))(iVar3);
    *(undefined4 *)((int)param_1 + 0x280) = 1;
  }
  return 0;
}

/* address: 0x00418120 */
/* name: CCockpit__AdvanceOpenCloseAnimationState */
/* signature: int __fastcall CCockpit__AdvanceOpenCloseAnimationState(void * param_1) */


int __fastcall CCockpit__AdvanceOpenCloseAnimationState(void *param_1)

{
  int *piVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  void *unaff_EDI;
  undefined *puVar5;
  void *pvVar6;
  char *pcVar7;

  piVar1 = (int *)((int)param_1 + 8);
  iVar2 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar2 == -1) {
    return 1;
  }
  pcVar7 = s_opening_00623ba4;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    puVar5 = &DAT_00623bb4;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(&DAT_00623bb4,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)puVar5,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x254) = 2;
    return 0;
  }
  pcVar7 = s_closing_00623b80;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar7 = s_closed_00623aec;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_closed_00623aec,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar7,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x254) = 3;
    return 0;
  }
  pcVar7 = s_unshutting_00623b74;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar7 = s_notshut_00623ae4;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_notshut_00623ae4,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar7,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x264) = 3;
    return 0;
  }
  pcVar7 = s_shutting_00623b88;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    puVar5 = &DAT_00623bac;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(&DAT_00623bac,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)puVar5,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x264) = 1;
    return 0;
  }
  iVar2 = CUnitAI__Helper_004fdeb0(param_1);
  return iVar2;
}

/* address: 0x004289b0 */
/* name: CUnitAI__AdvanceActivationAnimationState */
/* signature: int __fastcall CUnitAI__AdvanceActivationAnimationState(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnitAI__AdvanceActivationAnimationState(void *param_1)

{
  int *piVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  void *unaff_EDI;
  char *pcVar5;
  void *pvVar6;
  undefined **ppuVar7;

  piVar1 = (int *)((int)param_1 + 8);
  iVar2 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar2 == -1) {
    return 1;
  }
  ppuVar7 = &PTR_DAT_006248e8;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)ppuVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar5 = s_retract_006248e0;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_retract_006248e0,1,0);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar5,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 700) = 0;
    return 0;
  }
  pcVar5 = s_retract_006248e0;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar5,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar5 = s_normal_006239e4;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_normal_006239e4,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar5,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    return 0;
  }
  pcVar5 = s_Activate_00623e14;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar5,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar5 = s_Activated_006247d4;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_Activated_006247d4,1,1)
    ;
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar5,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x264) = 0;
    *(float *)((int)param_1 + 0x268) = DAT_00672fd0;
    VFuncSlot_22_004fd6a0((int)param_1);
    return 0;
  }
  pcVar5 = s_Deactivated_006248c8;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar5,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar5 = s_Normal_006247cc;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_Normal_006247cc,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar5,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x264) = 1;
    *(float *)((int)param_1 + 0x268) = DAT_00672fd0 + _DAT_005d8ba0;
    VFuncSlot_23_004fd700((int)param_1);
    return 0;
  }
  iVar2 = CUnitAI__Helper_004fdeb0(param_1);
  return iVar2;
}

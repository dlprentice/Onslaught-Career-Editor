/* address: 0x004fdeb0 */
/* name: CUnitAI__Helper_004fdeb0 */
/* signature: int __fastcall CUnitAI__Helper_004fdeb0(void * param_1) */


int __fastcall CUnitAI__Helper_004fdeb0(void *param_1)

{
  int *piVar1;
  int iVar2;
  void *pvVar3;
  int iVar4;
  int *piVar5;
  void *unaff_EDI;
  void *pvVar6;
  char *pcVar7;

  piVar1 = (int *)((int)param_1 + 8);
  iVar2 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar2 == -1) {
    return 1;
  }
  pcVar7 = s_deploying_006239cc;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar7 = s_deployed_006239ec;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_deployed_006239ec,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar7,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x244) = 4;
    return 0;
  }
  pcVar7 = s_undeploying_006239d8;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pvVar6 = (void *)0x1;
    pcVar7 = s_normal_006239e4;
    pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_normal_006239e4,1,1);
    iVar4 = FindAnimationIndex(pvVar3,(int)pcVar7,pvVar6);
    (**(code **)(iVar2 + 0xf0))(iVar4);
    *(undefined4 *)((int)param_1 + 0x244) = 0;
    return 0;
  }
  pcVar7 = s_prefire_0062cb60;
  pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
  iVar4 = (**(code **)(*piVar1 + 0x58))();
  piVar5 = *(int **)((int)param_1 + 0x30);
  if (iVar4 == iVar2) {
    iVar2 = *(int *)param_1;
    pcVar7 = s_prefirehold_00633c70;
  }
  else {
    pcVar7 = s_firing_0062cb68;
    pvVar3 = (void *)(**(code **)(*piVar5 + 0x24))();
    iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
    iVar4 = (**(code **)(*piVar1 + 0x58))();
    if (iVar4 != iVar2) {
      pcVar7 = s_postfire_0062cb70;
      pvVar3 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
      iVar2 = FindAnimationIndex(pvVar3,(int)pcVar7,unaff_EDI);
      iVar4 = (**(code **)(*piVar1 + 0x58))();
      if (iVar4 != iVar2) {
        iVar2 = CUnit__ResumeSavedScriptIfPresent((int)param_1);
        return iVar2;
      }
    }
    piVar5 = *(int **)((int)param_1 + 0x30);
    iVar2 = *(int *)param_1;
    pvVar3 = (void *)0x1;
    if (*(int *)((int)param_1 + 0x244) == 0) {
      pcVar7 = s_normal_006239e4;
      pvVar6 = (void *)(**(code **)(*piVar5 + 0x24))(s_normal_006239e4,1,1);
      goto LAB_004fe00f;
    }
    pcVar7 = s_deployed_006239ec;
  }
  pvVar3 = (void *)0x1;
  pvVar6 = (void *)(**(code **)(*piVar5 + 0x24))(pcVar7,1,1);
LAB_004fe00f:
  iVar4 = FindAnimationIndex(pvVar6,(int)pcVar7,pvVar3);
  (**(code **)(iVar2 + 0xf0))(iVar4);
  return 0;
}

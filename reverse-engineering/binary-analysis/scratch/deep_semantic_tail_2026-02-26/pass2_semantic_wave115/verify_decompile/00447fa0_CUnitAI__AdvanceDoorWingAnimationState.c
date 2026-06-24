/* address: 0x00447fa0 */
/* name: CUnitAI__AdvanceDoorWingAnimationState */
/* signature: int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * param_1) */


int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  int *piVar4;
  void *unaff_EDI;
  void *pvVar5;
  char *pcVar6;

  iVar1 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar1 == -1) {
    return 1;
  }
  pcVar6 = s_dooropening_00628a98;
  pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,unaff_EDI);
  if (iVar1 != iVar3) {
    pcVar6 = s_doorclosing_00628a8c;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,unaff_EDI);
    if (iVar1 == iVar3) {
      iVar1 = *(int *)param_1;
      pvVar5 = (void *)0x1;
      pcVar6 = s_doorclosed_00628a80;
      pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                                 (s_doorclosed_00628a80,1,1);
      iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,pvVar5);
      (**(code **)(iVar1 + 0xf0))(iVar3);
      (**(code **)(*(int *)param_1 + 0x1e0))();
      return 0;
    }
    pcVar6 = s_wingfolded_00628aa4;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,unaff_EDI);
    piVar4 = *(int **)((int)param_1 + 0x30);
    if (iVar1 == iVar3) {
      iVar1 = *(int *)param_1;
      pcVar6 = s_doorclosed_00628a80;
    }
    else {
      pcVar6 = s_wingunfolded_00628ab0;
      pvVar2 = (void *)(**(code **)(*piVar4 + 0x24))();
      iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,unaff_EDI);
      if (iVar1 != iVar3) {
        return 0;
      }
      piVar4 = *(int **)((int)param_1 + 0x30);
      iVar1 = *(int *)param_1;
      pcVar6 = s_wingflat_00628a74;
    }
    pvVar5 = (void *)0x1;
    pvVar2 = (void *)(**(code **)(*piVar4 + 0x24))(pcVar6,1,1);
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,pvVar5);
    (**(code **)(iVar1 + 0xf0))(iVar3);
    return 0;
  }
  iVar1 = *(int *)param_1;
  pvVar5 = (void *)0x1;
  pcVar6 = s_dooropen_00628ac0;
  pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_dooropen_00628ac0,1,1);
  iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,pvVar5);
  (**(code **)(iVar1 + 0xf0))(iVar3);
  *(undefined4 *)((int)param_1 + 0x27c) = 4;
  return 0;
}

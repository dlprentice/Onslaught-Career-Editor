/* address: 0x00415970 */
/* name: CUnitAI__Unk_00415970 */
/* signature: int __fastcall CUnitAI__Unk_00415970(void * param_1) */


int __fastcall CUnitAI__Unk_00415970(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  void *unaff_EDI;
  void *pvVar4;
  char *pcVar5;

  iVar1 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar1 == -1) {
    return 1;
  }
  pcVar5 = s_deploying_006239cc;
  pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_EDI);
  iVar3 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar3 == iVar1) {
    iVar1 = *(int *)param_1;
    pvVar4 = (void *)0x1;
    pcVar5 = s_deployed_006239ec;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_deployed_006239ec,1,1);
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar5,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar3);
    *(undefined4 *)((int)param_1 + 0x1f0) = 1;
    return 0;
  }
  pcVar5 = s_undeploying_006239d8;
  pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
  iVar1 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_EDI);
  iVar3 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar3 == iVar1) {
    iVar1 = *(int *)param_1;
    pvVar4 = (void *)0x1;
    pcVar5 = s_normal_006239e4;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_normal_006239e4,1,1);
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar5,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar3);
    *(undefined4 *)((int)param_1 + 0x260) = 0;
    return 0;
  }
  iVar1 = CUnitAI__Helper_004fdeb0(param_1);
  return iVar1;
}

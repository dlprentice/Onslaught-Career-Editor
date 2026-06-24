/* address: 0x0047d420 */
/* name: CUnitAI__QueueFiringOrPostfireAnimation */
/* signature: void __fastcall CUnitAI__QueueFiringOrPostfireAnimation(void * param_1) */


void __fastcall CUnitAI__QueueFiringOrPostfireAnimation(void *param_1)

{
  void *pvVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  void *unaff_EDI;
  void *pvVar5;
  char *pcVar6;

  CUnitAI__Helper_004fc170((int)param_1);
  if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x1c) == 0) {
    pcVar6 = s_firing_0062cb68;
    pvVar1 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
    iVar2 = FindAnimationIndex(pvVar1,(int)pcVar6,unaff_EDI);
    if (iVar2 == -1) {
      return;
    }
    piVar4 = *(int **)((int)param_1 + 0x30);
    iVar2 = *(int *)param_1;
    pcVar6 = s_firing_0062cb68;
  }
  else {
    pcVar6 = s_postfire_0062cb70;
    pvVar1 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
    iVar2 = FindAnimationIndex(pvVar1,(int)pcVar6,unaff_EDI);
    if (iVar2 == -1) {
      return;
    }
    piVar4 = *(int **)((int)param_1 + 0x30);
    iVar2 = *(int *)param_1;
    pcVar6 = s_postfire_0062cb70;
  }
  pvVar5 = (void *)0x1;
  pvVar1 = (void *)(**(code **)(*piVar4 + 0x24))(pcVar6,1,0);
  iVar3 = FindAnimationIndex(pvVar1,(int)pcVar6,pvVar5);
  (**(code **)(iVar2 + 0xf0))(iVar3);
  return;
}

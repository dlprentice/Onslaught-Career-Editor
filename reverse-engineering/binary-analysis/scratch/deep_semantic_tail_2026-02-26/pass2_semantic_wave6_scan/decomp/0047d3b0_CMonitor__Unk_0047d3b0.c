/* address: 0x0047d3b0 */
/* name: CMonitor__Unk_0047d3b0 */
/* signature: int __fastcall CMonitor__Unk_0047d3b0(void * param_1) */


int __fastcall CMonitor__Unk_0047d3b0(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  int iVar4;
  void *unaff_EDI;
  void *pvVar5;
  char *pcVar6;

  iVar1 = CUnit__Unk_004fbcb0(param_1);
  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x108) == 0) ||
     (*(int *)((int)param_1 + 0x244) == 4)) {
    pcVar6 = s_prefire_0062cb60;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar6,unaff_EDI);
    if (iVar3 != -1) {
      iVar3 = *(int *)param_1;
      pvVar5 = (void *)0x1;
      pcVar6 = s_prefire_0062cb60;
      pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_prefire_0062cb60,1,0)
      ;
      iVar4 = FindAnimationIndex(pvVar2,(int)pcVar6,pvVar5);
      (**(code **)(iVar3 + 0xf0))(iVar4);
      return iVar1;
    }
  }
  return iVar1;
}

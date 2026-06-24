/* address: 0x00489de0 */
/* name: CUnitAI__PromoteDieAnimationToDeadVariant */
/* signature: int __fastcall CUnitAI__PromoteDieAnimationToDeadVariant(void * param_1) */


int __fastcall CUnitAI__PromoteDieAnimationToDeadVariant(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  void *this;
  int iVar4;
  void *unaff_EDI;
  char *pcVar5;

  iVar1 = (**(code **)(*(int *)((int)param_1 + 8) + 0x58))();
  if (iVar1 != -1) {
    pcVar5 = s_die_up_0062d560;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_EDI);
    if (iVar1 == iVar3) {
      iVar3 = *(int *)param_1;
      pvVar2 = (void *)0x1;
      pcVar5 = s_dead_up_0062d528;
      this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_dead_up_0062d528,1,1);
    }
    else {
      pcVar5 = s_die_back_0062d530;
      pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
      iVar3 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_EDI);
      if (iVar1 == iVar3) {
        iVar3 = *(int *)param_1;
        pvVar2 = (void *)0x1;
        pcVar5 = s_dead_back_0062d4f4;
        this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                                 (s_dead_back_0062d4f4,1,1);
      }
      else {
        pcVar5 = s_die_left_0062d53c;
        pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
        iVar3 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_EDI);
        if (iVar1 == iVar3) {
          iVar3 = *(int *)param_1;
          pvVar2 = (void *)0x1;
          pcVar5 = s_dead_left_0062d500;
          this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                                   (s_dead_left_0062d500,1,1);
        }
        else {
          pcVar5 = s_die_right_0062d548;
          pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
          iVar4 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_EDI);
          iVar3 = *(int *)param_1;
          pvVar2 = (void *)0x1;
          if (iVar1 == iVar4) {
            pcVar5 = s_dead_right_0062d50c;
            this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
          }
          else {
            pcVar5 = s_dead_forward_0062d518;
            this = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                                     (s_dead_forward_0062d518,1,1);
          }
        }
      }
    }
    iVar1 = FindAnimationIndex(this,(int)pcVar5,pvVar2);
    (**(code **)(iVar3 + 0xf0))(iVar1);
  }
  return 0;
}

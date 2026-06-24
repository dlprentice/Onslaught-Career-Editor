/* address: 0x004178a0 */
/* name: CUnit__ProcessClosingAndUnshuttingAnimations */
/* signature: void __fastcall CUnit__ProcessClosingAndUnshuttingAnimations(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__ProcessClosingAndUnshuttingAnimations(void *param_1)

{
  int iVar1;
  void *pvVar2;
  int iVar3;
  void *unaff_ESI;
  void *pvVar4;
  char *pcVar5;

  CUnit__Unk_004fa800(param_1);
  if (*(int *)((int)param_1 + 0x254) == 2) {
    iVar1 = CUnit__Unk_004fd7a0((int)param_1);
    if (iVar1 == 0) {
      if ((*(float *)((int)param_1 + 0x25c) < DAT_00672fd0) && (*(int *)((int)param_1 + 0x254) == 2)
         ) {
        pcVar5 = s_closing_00623b80;
        pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))();
        iVar1 = FindAnimationIndex(pvVar2,(int)pcVar5,unaff_ESI);
        if (iVar1 == -1) {
          *(undefined4 *)((int)param_1 + 0x254) = 3;
        }
        else {
          *(undefined4 *)((int)param_1 + 0x254) = 1;
          (**(code **)(*(int *)param_1 + 0xf0))(iVar1,1,0);
        }
      }
    }
    else {
      *(float *)((int)param_1 + 0x25c) = DAT_00672fd0 + _DAT_005d8c44;
    }
  }
  else {
    iVar1 = CUnit__Unk_004fd7a0((int)param_1);
    if (iVar1 != 0) {
      (**(code **)(*(int *)param_1 + 0x1cc))();
    }
  }
  if (((*(int *)((int)param_1 + 0x260) != 0) && (*(int *)((int)param_1 + 0x264) == 1)) &&
     (*(float *)((int)param_1 + 0x268) + _DAT_005d85d4 < DAT_00672fd0)) {
    iVar1 = *(int *)param_1;
    pvVar4 = (void *)0x1;
    pcVar5 = s_unshutting_00623b74;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))
                               (s_unshutting_00623b74,1,0);
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar5,pvVar4);
    (**(code **)(iVar1 + 0xf0))(iVar3);
    *(undefined4 *)((int)param_1 + 0x264) = 2;
  }
  return;
}

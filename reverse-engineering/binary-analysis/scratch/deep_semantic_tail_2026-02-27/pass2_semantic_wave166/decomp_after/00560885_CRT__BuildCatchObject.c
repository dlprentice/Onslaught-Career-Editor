/* address: 0x00560885 */
/* name: CRT__BuildCatchObject */
/* signature: void __cdecl CRT__BuildCatchObject(int param_1, int param_2, void * param_3, void * param_4) */


void __cdecl CRT__BuildCatchObject(int param_1,int param_2,void *param_3,void *param_4)

{
  int *piVar1;
  bool bVar2;
  undefined3 extraout_var;
  undefined3 extraout_var_00;
  int iVar3;
  undefined3 extraout_var_01;
  undefined3 extraout_var_02;
  undefined3 extraout_var_03;
  undefined3 extraout_var_04;
  void *pvVar4;
  undefined3 extraout_var_05;
  undefined3 extraout_var_06;
  undefined3 extraout_var_07;
  uint uVar5;
  void *local_14;
  undefined1 *puStack_10;
  undefined *puStack_c;
  undefined4 local_8;

  puStack_c = &DAT_005e5b60;
  puStack_10 = &LAB_0056127c;
  local_14 = ExceptionList;
  if (*(int *)((int)param_3 + 4) == 0) {
    return;
  }
  if (*(char *)(*(int *)((int)param_3 + 4) + 8) == '\0') {
    return;
  }
  if (*(int *)((int)param_3 + 8) == 0) {
    return;
  }
  piVar1 = (int *)(*(int *)((int)param_3 + 8) + 0xc + param_2);
  local_8 = 0;
  if ((*(byte *)param_3 & 8) == 0) {
    if ((*(byte *)param_4 & 1) == 0) {
      if (*(int *)((int)param_4 + 0x18) == 0) {
        ExceptionList = &local_14;
        bVar2 = CRT__IsReadablePtr(*(void **)(param_1 + 0x18),1);
        if ((CONCAT31(extraout_var_03,bVar2) != 0) &&
           (bVar2 = CRT__IsWritablePtr((int)piVar1,1), CONCAT31(extraout_var_04,bVar2) != 0)) {
          uVar5 = *(uint *)((int)param_4 + 0x14);
          pvVar4 = (void *)CRT__AdjustPointerByPMD
                                     (*(int *)(param_1 + 0x18),(void *)((int)param_4 + 8));
          CRT__MemMoveOverlapSafe(piVar1,pvVar4,uVar5);
          ExceptionList = local_14;
          return;
        }
      }
      else {
        ExceptionList = &local_14;
        bVar2 = CRT__IsReadablePtr(*(void **)(param_1 + 0x18),1);
        if (((CONCAT31(extraout_var_05,bVar2) != 0) &&
            (bVar2 = CRT__IsWritablePtr((int)piVar1,1), CONCAT31(extraout_var_06,bVar2) != 0)) &&
           (bVar2 = CRT__IsExecutablePtr(*(int *)((int)param_4 + 0x18)),
           CONCAT31(extraout_var_07,bVar2) != 0)) {
          if ((*(byte *)param_4 & 4) != 0) {
            CRT__AdjustPointerByPMD(*(int *)(param_1 + 0x18),(void *)((int)param_4 + 8));
            CRT__SehLockUnlockAndJump((int)piVar1,*(void **)((int)param_4 + 0x18));
            ExceptionList = local_14;
            return;
          }
          CRT__AdjustPointerByPMD(*(int *)(param_1 + 0x18),(void *)((int)param_4 + 8));
          CRT__InvokeCallbackWithLockGuards((int)piVar1,*(void **)((int)param_4 + 0x18));
          ExceptionList = local_14;
          return;
        }
      }
    }
    else {
      ExceptionList = &local_14;
      bVar2 = CRT__IsReadablePtr(*(void **)(param_1 + 0x18),1);
      if ((CONCAT31(extraout_var_01,bVar2) != 0) &&
         (bVar2 = CRT__IsWritablePtr((int)piVar1,1), CONCAT31(extraout_var_02,bVar2) != 0)) {
        CRT__MemMoveOverlapSafe(piVar1,*(void **)(param_1 + 0x18),*(uint *)((int)param_4 + 0x14));
        if (*(int *)((int)param_4 + 0x14) != 4) {
          ExceptionList = local_14;
          return;
        }
        iVar3 = *piVar1;
        if (iVar3 == 0) {
          ExceptionList = local_14;
          return;
        }
        goto LAB_00560913;
      }
    }
  }
  else {
    ExceptionList = &local_14;
    bVar2 = CRT__IsReadablePtr(*(void **)(param_1 + 0x18),1);
    if ((CONCAT31(extraout_var,bVar2) != 0) &&
       (bVar2 = CRT__IsWritablePtr((int)piVar1,1), CONCAT31(extraout_var_00,bVar2) != 0)) {
      iVar3 = *(int *)(param_1 + 0x18);
      *piVar1 = iVar3;
LAB_00560913:
      iVar3 = CRT__AdjustPointerByPMD(iVar3,(void *)((int)param_4 + 8));
      *piVar1 = iVar3;
      ExceptionList = local_14;
      return;
    }
  }
  CDXTexture__InvokeGlobalCleanupCallbackAndFinalize();
  ExceptionList = local_14;
  return;
}

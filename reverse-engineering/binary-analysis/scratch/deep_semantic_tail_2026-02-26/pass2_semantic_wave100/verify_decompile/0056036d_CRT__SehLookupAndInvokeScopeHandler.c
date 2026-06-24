/* address: 0x0056036d */
/* name: CRT__SehLookupAndInvokeScopeHandler */
/* signature: int CRT__SehLookupAndInvokeScopeHandler(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__SehLookupAndInvokeScopeHandler(void)

{
  void *pvVar1;
  bool bVar2;
  int iVar3;
  undefined3 extraout_var;
  int *piVar4;
  int extraout_EAX;
  int extraout_EAX_00;
  int *piVar5;
  int *in_stack_00000004;
  int in_stack_00000008;
  int in_stack_00000014;
  char in_stack_00000018;
  int in_stack_0000001c;
  uint local_1c;
  uint local_18;
  int local_14;
  int local_10;
  int local_c;
  uint local_8;

  local_18 = local_18 & 0xffffff00;
  local_14 = *(int *)(in_stack_00000008 + 8);
  if ((local_14 < -1) || (*(int *)(in_stack_00000014 + 4) <= local_14)) {
    CDXTexture__InvokeGlobalCleanupCallbackAndFinalize();
  }
  if (*in_stack_00000004 == -0x1f928c9d) {
    if (((in_stack_00000004[4] == 3) && (in_stack_00000004[5] == 0x19930520)) &&
       (in_stack_00000004[7] == 0)) {
      iVar3 = CTexture__Helper_00560b93();
      if (*(int *)(iVar3 + 0x6c) == 0) {
        return iVar3;
      }
      iVar3 = CTexture__Helper_00560b93();
      in_stack_00000004 = *(int **)(iVar3 + 0x6c);
      CTexture__Helper_00560b93();
      local_18 = CONCAT31(local_18._1_3_,1);
      bVar2 = CDXTexture__Unk_005693e2(in_stack_00000004,1);
      if (CONCAT31(extraout_var,bVar2) == 0) {
        CDXTexture__InvokeGlobalCleanupCallbackAndFinalize();
      }
      if (*in_stack_00000004 != -0x1f928c9d) goto LAB_005604f5;
      if (((in_stack_00000004[4] == 3) && (in_stack_00000004[5] == 0x19930520)) &&
         (in_stack_00000004[7] == 0)) {
        CDXTexture__InvokeGlobalCleanupCallbackAndFinalize();
      }
    }
    iVar3 = local_14;
    if (((*in_stack_00000004 == -0x1f928c9d) && (in_stack_00000004[4] == 3)) &&
       (in_stack_00000004[5] == 0x19930520)) {
      piVar4 = (int *)CDXTexture__Helper_0055d90b
                                (in_stack_00000014,in_stack_0000001c,local_14,&local_8,&local_1c);
      do {
        if (local_1c <= local_8) {
          if (in_stack_00000018 == '\0') {
            return local_8;
          }
          CDXTexture__Helper_00560a49((int)in_stack_00000004);
          return extraout_EAX;
        }
        if ((*piVar4 <= iVar3) && (iVar3 <= piVar4[1])) {
          pvVar1 = (void *)piVar4[4];
          for (local_10 = piVar4[3]; iVar3 = local_14, 0 < local_10; local_10 = local_10 + -1) {
            piVar5 = *(int **)(in_stack_00000004[7] + 0xc);
            for (local_c = *piVar5; 0 < local_c; local_c = local_c + -1) {
              piVar5 = piVar5 + 1;
              iVar3 = CDXTexture__Helper_005605ca
                                (pvVar1,(void *)*piVar5,(void *)in_stack_00000004[7]);
              if (iVar3 != 0) {
                CRT__SehUnwindAndResumeSearch();
                iVar3 = local_14;
                goto LAB_005604d5;
              }
            }
            pvVar1 = (void *)((int)pvVar1 + 0x10);
          }
        }
LAB_005604d5:
        local_8 = local_8 + 1;
        piVar4 = piVar4 + 5;
      } while( true );
    }
  }
LAB_005604f5:
  if (in_stack_00000018 == '\0') {
    iVar3 = CDXTexture__Helper_00560520();
    return iVar3;
  }
  CDXTexture__InvokeTlsCleanupCallbackAndFinalize();
  return extraout_EAX_00;
}

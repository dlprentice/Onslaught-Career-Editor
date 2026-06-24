/* address: 0x0059930d */
/* name: CTexture__ValidateConstantRegisterDeclarationType */
/* signature: int __thiscall CTexture__ValidateConstantRegisterDeclarationType(void * this, void * param_1, void * param_2, void * param_3, void * param_4) */


int __thiscall
CTexture__ValidateConstantRegisterDeclarationType
          (void *this,void *param_1,void *param_2,void *param_3,void *param_4)

{
  int iVar1;
  int *extraout_EDX;
  int *piVar2;
  int *piVar3;
  char *pcVar4;
  int local_24 [8];

  piVar2 = param_1;
  piVar3 = local_24;
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *piVar3 = *piVar2;
    piVar2 = piVar2 + 1;
    piVar3 = piVar3 + 1;
  }
  local_24[2] = (int)param_2 + 2;
  local_24[0] = 10;
  iVar1 = CFastVB__SelectBestNodeTreeMatch();
  if (iVar1 == 0) {
    iVar1 = CFastVB__ComputeNodeSpanAndStride(*(int *)((int)param_2 + 0x20),param_3,(void *)0x0);
    if (iVar1 < 0) {
      return iVar1;
    }
    if (*(short *)param_2 == DAT_005ecf10) {
      if (((*extraout_EDX != 1) || (iVar1 = *(int *)((int)param_2 + 0x20), *(int *)(iVar1 + 4) != 8)
          ) || ((*(int *)(iVar1 + 0x10) != 0 || (*(int *)(iVar1 + 0x14) != 0)))) {
        pcVar4 = "boolean constant register \'%s\' must be defined as a variable of type bool only";
        iVar1 = 0xb54;
LAB_005993e8:
        CTexture__AppendDiagnosticMessage
                  ((void *)(*(int *)(*(int *)this + 4) + 4),(int)param_1,iVar1,(int)pcVar4);
        return -0x7fffbffb;
      }
    }
    else if ((*(short *)param_2 == DAT_005ecf0c) &&
            ((((*extraout_EDX != 1 ||
               (iVar1 = *(int *)((int)param_2 + 0x20), *(int *)(iVar1 + 4) != 8)) ||
              (*(int *)(iVar1 + 0x10) != 1)) ||
             ((*(int *)(iVar1 + 0x14) != 4 || (*(uint *)(iVar1 + 0x1c) < 3)))))) {
      pcVar4 =
      "integer constant register \'%s\' must be defined as a variable of type int3 or int4 only";
      iVar1 = 0xb55;
      goto LAB_005993e8;
    }
  }
  else {
    *(undefined4 *)param_3 = 0;
  }
  return 0;
}

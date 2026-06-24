/* address: 0x00440ad0 */
/* name: CUnitAI__Unk_00440ad0 */
/* signature: void __stdcall CUnitAI__Unk_00440ad0(void * param_1, int param_2, int param_3, int param_4) */


void CUnitAI__Unk_00440ad0(void *param_1,int param_2,int param_3,int param_4)

{
  undefined2 uVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  short *psVar5;
  int iVar6;
  short sVar7;
  int iVar8;
  int iVar9;
  int local_4;

  iVar4 = param_2;
  iVar8 = param_2 + 1;
  if (0 < param_3) {
    param_2 = 0;
    local_4 = param_3;
    psVar5 = param_1;
    do {
      iVar6 = param_2;
      iVar9 = iVar4;
      if (0 < iVar4) {
        do {
          sVar2 = (short)iVar6;
          sVar3 = (short)iVar8;
          sVar7 = sVar2 + 1 + sVar3;
          psVar5[1] = sVar2 + sVar3;
          *psVar5 = sVar2;
          psVar5[2] = sVar7;
          psVar5[3] = sVar2;
          psVar5[5] = sVar2 + 1;
          psVar5[4] = sVar7;
          psVar5 = psVar5 + 6;
          iVar9 = iVar9 + -1;
          iVar6 = iVar6 + 1;
        } while (iVar9 != 0);
      }
      param_2 = param_2 + iVar8;
      local_4 = local_4 + -1;
    } while (local_4 != 0);
  }
  if (param_4 != 0) {
    for (iVar8 = iVar4 * param_3 * 2; iVar8 != 0; iVar8 = iVar8 + -1) {
      uVar1 = *(undefined2 *)param_1;
      *(undefined2 *)param_1 = *(undefined2 *)((int)param_1 + 2);
      *(undefined2 *)((int)param_1 + 2) = uVar1;
      param_1 = (void *)((int)param_1 + 6);
    }
  }
  return;
}

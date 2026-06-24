/* address: 0x005723c0 */
/* name: CTexture__Helper_005723c0 */
/* signature: double __stdcall CTexture__Helper_005723c0(void * param_1, int param_2) */


double CTexture__Helper_005723c0(void *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  uint uVar5;
  int local_c;
  int local_8;

  uVar5 = 0;
  local_c = 0;
  local_8 = 0;
  do {
    if ((*(int *)(param_2 + 0x10) == 0) ||
       ((uint)(*(int *)(param_2 + 0x14) - *(int *)(param_2 + 0x10) >> 2) <= uVar5)) {
      return (double)local_c / (double)local_8;
    }
    iVar1 = *(int *)(param_2 + 0x10);
    iVar2 = *(int *)((int)param_1 + 4);
    iVar3 = 0;
    if (0 < iVar2) {
      piVar4 = *(int **)param_1;
      do {
        if (*piVar4 == **(int **)(iVar1 + uVar5 * 4)) {
          local_c = local_c + 1;
          break;
        }
        iVar3 = iVar3 + 1;
        piVar4 = piVar4 + 1;
      } while (iVar3 < iVar2);
    }
    iVar3 = 0;
    if (0 < iVar2) {
      piVar4 = *(int **)param_1;
      do {
        if (*piVar4 == *(int *)(*(int *)(iVar1 + uVar5 * 4) + 4)) {
          local_c = local_c + 1;
          break;
        }
        iVar3 = iVar3 + 1;
        piVar4 = piVar4 + 1;
      } while (iVar3 < iVar2);
    }
    iVar3 = 0;
    if (0 < iVar2) {
      piVar4 = *(int **)param_1;
      do {
        if (*piVar4 == *(int *)(*(int *)(iVar1 + uVar5 * 4) + 8)) {
          local_c = local_c + 1;
          break;
        }
        iVar3 = iVar3 + 1;
        piVar4 = piVar4 + 1;
      } while (iVar3 < iVar2);
    }
    local_8 = local_8 + 1;
    uVar5 = uVar5 + 1;
  } while( true );
}

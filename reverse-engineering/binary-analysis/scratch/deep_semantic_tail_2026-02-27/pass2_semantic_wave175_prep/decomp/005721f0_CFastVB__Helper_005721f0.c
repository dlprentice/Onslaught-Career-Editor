/* address: 0x005721f0 */
/* name: CFastVB__Helper_005721f0 */
/* signature: void __stdcall CFastVB__Helper_005721f0(void * param_1, int param_2) */


void CFastVB__Helper_005721f0(void *param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;

  uVar5 = 0;
LAB_005721ff:
  do {
    iVar3 = *(int *)(param_2 + 0x10);
    if ((iVar3 == 0) || ((uint)(*(int *)(param_2 + 0x14) - iVar3 >> 2) <= uVar5)) {
      return;
    }
    iVar2 = *(int *)((int)param_1 + 4);
    iVar6 = 0;
    if (0 < iVar2) {
      piVar4 = *(int **)param_1;
      do {
        if (*piVar4 == **(int **)(iVar3 + uVar5 * 4)) goto LAB_00572263;
        iVar6 = iVar6 + 1;
        piVar4 = piVar4 + 1;
      } while (iVar6 < iVar2);
    }
    iVar2 = iVar2 + -2;
    uVar1 = **(undefined4 **)(iVar3 + uVar5 * 4);
    while (-1 < iVar2) {
      iVar2 = iVar2 + -1;
      *(undefined4 *)(*(int *)param_1 + 8 + iVar2 * 4) =
           *(undefined4 *)(*(int *)param_1 + 4 + iVar2 * 4);
    }
    **(undefined4 **)param_1 = uVar1;
LAB_00572263:
    iVar3 = *(int *)((int)param_1 + 4);
    iVar2 = 0;
    if (0 < iVar3) {
      piVar4 = *(int **)param_1;
      do {
        if (*piVar4 == *(int *)(*(int *)(*(int *)(param_2 + 0x10) + uVar5 * 4) + 4))
        goto LAB_005722ab;
        iVar2 = iVar2 + 1;
        piVar4 = piVar4 + 1;
      } while (iVar2 < iVar3);
    }
    iVar3 = iVar3 + -2;
    uVar1 = *(undefined4 *)(*(int *)(*(int *)(param_2 + 0x10) + uVar5 * 4) + 4);
    while (-1 < iVar3) {
      iVar3 = iVar3 + -1;
      *(undefined4 *)(*(int *)param_1 + 8 + iVar3 * 4) =
           *(undefined4 *)(*(int *)param_1 + 4 + iVar3 * 4);
    }
    **(undefined4 **)param_1 = uVar1;
LAB_005722ab:
    iVar3 = *(int *)((int)param_1 + 4);
    iVar2 = 0;
    if (0 < iVar3) {
      piVar4 = *(int **)param_1;
      do {
        if (*piVar4 == *(int *)(*(int *)(*(int *)(param_2 + 0x10) + uVar5 * 4) + 8)) {
          uVar5 = uVar5 + 1;
          goto LAB_005721ff;
        }
        iVar2 = iVar2 + 1;
        piVar4 = piVar4 + 1;
      } while (iVar2 < iVar3);
    }
    iVar3 = iVar3 + -2;
    uVar1 = *(undefined4 *)(*(int *)(*(int *)(param_2 + 0x10) + uVar5 * 4) + 8);
    while (-1 < iVar3) {
      iVar3 = iVar3 + -1;
      *(undefined4 *)(*(int *)param_1 + 8 + iVar3 * 4) =
           *(undefined4 *)(*(int *)param_1 + 4 + iVar3 * 4);
    }
    uVar5 = uVar5 + 1;
    **(undefined4 **)param_1 = uVar1;
  } while( true );
}

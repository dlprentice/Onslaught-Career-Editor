/* address: 0x005b3440 */
/* name: CFastVB__Unk_005b3440 */
/* signature: int __stdcall CFastVB__Unk_005b3440(void * param_1, void * param_2, uint param_3, void * param_4) */


int CFastVB__Unk_005b3440(void *param_1,void *param_2,uint param_3,void *param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  int in_EAX;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;

  uVar6 = (int)*(short *)param_1 - (int)param_2;
  uVar3 = uVar6;
  if ((int)uVar6 < 0) {
    uVar3 = -uVar6;
    uVar6 = uVar6 - 1;
  }
  iVar5 = 0;
  if (uVar3 != 0) {
    do {
      uVar3 = (int)uVar3 >> 1;
      iVar5 = iVar5 + 1;
    } while (uVar3 != 0);
    if (0xb < iVar5) {
      piVar1 = *(int **)(in_EAX + 0x20);
      puVar2 = (undefined4 *)*piVar1;
      puVar2[5] = 6;
      (*(code *)*puVar2)(piVar1);
    }
  }
  iVar4 = CFastVB__Helper_005b3370(*(uint *)(param_3 + iVar5 * 4));
  if ((iVar4 != 0) && ((iVar5 == 0 || (iVar5 = CFastVB__Helper_005b3370(uVar6), iVar5 != 0)))) {
    iVar5 = 0;
    param_2 = &DAT_005f37fc;
    do {
      param_3 = (uint)*(short *)((int)param_1 + *(int *)param_2 * 2);
      if (param_3 == 0) {
        iVar5 = iVar5 + 1;
      }
      else {
        for (; 0xf < iVar5; iVar5 = iVar5 + -0x10) {
          iVar4 = CFastVB__Helper_005b3370(*(uint *)((int)param_4 + 0x3c0));
          if (iVar4 == 0) {
            return 0;
          }
        }
        uVar3 = param_3;
        if ((int)param_3 < 0) {
          uVar3 = -param_3;
          param_3 = param_3 - 1;
        }
        iVar7 = (int)uVar3 >> 1;
        iVar4 = 1;
        if (iVar7 != 0) {
          do {
            iVar7 = iVar7 >> 1;
            iVar4 = iVar4 + 1;
          } while (iVar7 != 0);
          if (10 < iVar4) {
            piVar1 = *(int **)(in_EAX + 0x20);
            puVar2 = (undefined4 *)*piVar1;
            puVar2[5] = 6;
            (*(code *)*puVar2)(piVar1);
          }
        }
        iVar5 = CFastVB__Helper_005b3370(*(uint *)((int)param_4 + (iVar5 * 0x10 + iVar4) * 4));
        if (iVar5 == 0) {
          return 0;
        }
        iVar5 = CFastVB__Helper_005b3370(param_3);
        if (iVar5 == 0) {
          return 0;
        }
        iVar5 = 0;
      }
      param_2 = (void *)((int)param_2 + 4);
    } while ((int)param_2 < 0x5f38f8);
    if ((iVar5 < 1) || (iVar5 = CFastVB__Helper_005b3370(*(uint *)param_4), iVar5 != 0)) {
      return 1;
    }
  }
  return 0;
}

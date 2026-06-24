/* address: 0x005b3840 */
/* name: CTexture__Helper_005b3840 */
/* signature: void __thiscall CTexture__Helper_005b3840(void * this, int param_1, void * param_2, void * param_3, void * param_4) */


void __thiscall
CTexture__Helper_005b3840(void *this,int param_1,void *param_2,void *param_3,void *param_4)

{
  undefined4 *puVar1;
  int in_EAX;
  int iVar2;
  int iVar3;
  int *piVar4;
  int iVar5;

  iVar2 = (int)*(short *)param_2 - (int)this;
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  iVar5 = 0;
  if (iVar2 != 0) {
    do {
      iVar2 = iVar2 >> 1;
      iVar5 = iVar5 + 1;
    } while (iVar2 != 0);
    if (0xb < iVar5) {
      puVar1 = *(undefined4 **)param_1;
      puVar1[5] = 6;
      (*(code *)*puVar1)(param_1);
    }
  }
  piVar4 = (int *)(in_EAX + iVar5 * 4);
  *piVar4 = *piVar4 + 1;
  iVar2 = 0;
  piVar4 = &DAT_005f37fc;
  do {
    iVar5 = (int)*(short *)((int)param_2 + *piVar4 * 2);
    if (iVar5 == 0) {
      iVar2 = iVar2 + 1;
    }
    else {
      if (0xf < iVar2) {
        iVar3 = (iVar2 - 0x10U >> 4) + 1;
        iVar2 = iVar2 + iVar3 * -0x10;
        *(int *)((int)param_3 + 0x3c0) = iVar3 + *(int *)((int)param_3 + 0x3c0);
      }
      if (iVar5 < 0) {
        iVar5 = -iVar5;
      }
      iVar5 = iVar5 >> 1;
      iVar3 = 1;
      if (iVar5 != 0) {
        do {
          iVar5 = iVar5 >> 1;
          iVar3 = iVar3 + 1;
        } while (iVar5 != 0);
        if (10 < iVar3) {
          puVar1 = *(undefined4 **)param_1;
          puVar1[5] = 6;
          (*(code *)*puVar1)(param_1);
        }
      }
      iVar3 = iVar2 * 0x10 + iVar3;
      *(int *)((int)param_3 + iVar3 * 4) = *(int *)((int)param_3 + iVar3 * 4) + 1;
      iVar2 = 0;
    }
    piVar4 = piVar4 + 1;
  } while ((int)piVar4 < 0x5f38f8);
  if (0 < iVar2) {
    *(int *)param_3 = *(int *)param_3 + 1;
  }
  return;
}

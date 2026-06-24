/* address: 0x00595550 */
/* name: CTexture__Helper_00595550 */
/* signature: void __stdcall CTexture__Helper_00595550(void * param_1, int param_2, int param_3, int param_4, int param_5) */


void CTexture__Helper_00595550(void *param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 extraout_EAX;
  int iVar4;
  int *piVar5;
  undefined2 *puVar6;

  iVar1 = *(int *)((int)param_1 + 0x14);
  if (iVar1 != 100) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x14;
    puVar2[6] = iVar1;
    (*(code *)*puVar2)(param_1);
  }
  if ((param_2 < 0) || (3 < param_2)) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x1f;
    puVar2[6] = param_2;
    (*(code *)*puVar2)(param_1);
  }
  if (*(int *)((int)param_1 + param_2 * 4 + 0x48) == 0) {
    CTexture__Helper_0059c630((int)param_1);
    *(undefined4 *)((int)param_1 + param_2 * 4 + 0x48) = extraout_EAX;
  }
  iVar1 = *(int *)((int)param_1 + param_2 * 4 + 0x48);
  puVar6 = (undefined2 *)(iVar1 + 4);
  piVar5 = (int *)(param_3 + 8);
  param_1 = (void *)0x8;
  do {
    iVar4 = (piVar5[-2] * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = piVar5[-1];
    puVar6[-2] = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = *piVar5;
    puVar6[-1] = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = piVar5[1];
    *puVar6 = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = piVar5[2];
    puVar6[1] = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = piVar5[3];
    puVar6[2] = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = piVar5[4];
    puVar6[3] = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    iVar3 = piVar5[5];
    puVar6[4] = (short)iVar4;
    iVar4 = (iVar3 * param_4 + 0x32) / 100;
    if (iVar4 < 1) {
      iVar4 = 1;
    }
    else if (0x7fff < iVar4) {
      iVar4 = 0x7fff;
    }
    if ((param_5 != 0) && (0xff < iVar4)) {
      iVar4 = 0xff;
    }
    puVar6[5] = (short)iVar4;
    piVar5 = piVar5 + 8;
    puVar6 = puVar6 + 8;
    param_1 = (void *)((int)param_1 + -1);
  } while (param_1 != (void *)0x0);
  *(undefined4 *)(iVar1 + 0x80) = 0;
  return;
}

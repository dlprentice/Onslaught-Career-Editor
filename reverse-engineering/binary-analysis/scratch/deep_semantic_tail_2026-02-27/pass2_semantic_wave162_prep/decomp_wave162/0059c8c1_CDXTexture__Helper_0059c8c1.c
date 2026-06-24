/* address: 0x0059c8c1 */
/* name: CDXTexture__Helper_0059c8c1 */
/* signature: int __stdcall CDXTexture__Helper_0059c8c1(void * param_1, int param_2) */


int CDXTexture__Helper_0059c8c1(void *param_1,int param_2)

{
  int *piVar1;
  byte bVar2;
  undefined4 uVar3;
  void *extraout_EAX;
  undefined4 *puVar4;
  void *pvVar5;
  void *pvVar6;

  if (((param_1 == (void *)0x0) ||
      (puVar4 = *(undefined4 **)((int)param_1 + 0x1c), puVar4 == (undefined4 *)0x0)) ||
     (*(int *)param_1 == 0)) {
LAB_0059caf8:
    return -2;
  }
  pvVar6 = (void *)0xfffffffb;
  pvVar5 = (void *)0x0;
  if (param_2 == 4) {
    pvVar5 = pvVar6;
  }
LAB_0059caeb:
  switch(*puVar4) {
  case 0:
    if (*(int *)((int)param_1 + 4) == 0) {
      return (int)pvVar6;
    }
    *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
    *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
    *(uint *)(*(int *)((int)param_1 + 0x1c) + 4) = (uint)**(byte **)param_1;
    puVar4 = *(undefined4 **)((int)param_1 + 0x1c);
    uVar3 = puVar4[1];
    *(int *)param_1 = *(int *)param_1 + 1;
    if (((byte)uVar3 & 0xf) == 8) {
      if (((uint)puVar4[1] >> 4) + 8 <= (uint)puVar4[4]) {
        *puVar4 = 1;
        pvVar6 = pvVar5;
        goto switchD_0059c8fe_caseD_1;
      }
      *puVar4 = 0xd;
      *(char **)((int)param_1 + 0x18) = "invalid window size";
    }
    else {
      *puVar4 = 0xd;
      *(char **)((int)param_1 + 0x18) = "unknown compression method";
    }
    goto LAB_0059cade;
  case 1:
switchD_0059c8fe_caseD_1:
    if (*(int *)((int)param_1 + 4) == 0) {
      return (int)pvVar6;
    }
    puVar4 = *(undefined4 **)((int)param_1 + 0x1c);
    *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
    *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
    bVar2 = **(byte **)param_1;
    *(byte **)param_1 = *(byte **)param_1 + 1;
    if ((puVar4[1] * 0x100 + (uint)bVar2) % 0x1f != 0) {
      *puVar4 = 0xd;
      *(char **)((int)param_1 + 0x18) = "incorrect header check";
      goto LAB_0059cade;
    }
    if ((bVar2 & 0x20) != 0) {
      **(undefined4 **)((int)param_1 + 0x1c) = 2;
      pvVar6 = pvVar5;
      goto switchD_0059c8fe_caseD_2;
    }
    *puVar4 = 7;
    pvVar6 = pvVar5;
    break;
  case 2:
switchD_0059c8fe_caseD_2:
    if (*(int *)((int)param_1 + 4) == 0) {
      return (int)pvVar6;
    }
    *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
    *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
    *(uint *)(*(int *)((int)param_1 + 0x1c) + 8) = (uint)**(byte **)param_1 << 0x18;
    *(int *)param_1 = *(int *)param_1 + 1;
    **(undefined4 **)((int)param_1 + 0x1c) = 3;
    pvVar6 = pvVar5;
  case 3:
    goto switchD_0059c8fe_caseD_3;
  case 4:
    goto switchD_0059c8fe_caseD_4;
  case 5:
    goto switchD_0059c8fe_caseD_5;
  case 6:
    **(undefined4 **)((int)param_1 + 0x1c) = 0xd;
    *(char **)((int)param_1 + 0x18) = "need dictionary";
    *(undefined4 *)(*(int *)((int)param_1 + 0x1c) + 4) = 0;
    return -2;
  case 7:
    CTexture__Helper_005b1e94(*(void **)(*(int *)((int)param_1 + 0x1c) + 0x14),param_1,pvVar6);
    if (extraout_EAX == (void *)0xfffffffd) {
      **(undefined4 **)((int)param_1 + 0x1c) = 0xd;
      *(undefined4 *)(*(int *)((int)param_1 + 0x1c) + 4) = 0;
      pvVar6 = (void *)0xfffffffd;
    }
    else {
      pvVar6 = extraout_EAX;
      if (extraout_EAX == (void *)0x0) {
        pvVar6 = pvVar5;
      }
      if (pvVar6 != (void *)0x1) {
        return (int)pvVar6;
      }
      CDXTexture__ResetDecodeWindowState
                (*(void **)(*(int *)((int)param_1 + 0x1c) + 0x14),(int)param_1,
                 (void *)(*(int *)((int)param_1 + 0x1c) + 4));
      puVar4 = *(undefined4 **)((int)param_1 + 0x1c);
      if (puVar4[3] == 0) {
        *puVar4 = 8;
        pvVar6 = pvVar5;
        goto switchD_0059c8fe_caseD_8;
      }
      *puVar4 = 0xc;
      pvVar6 = pvVar5;
    }
    break;
  case 8:
switchD_0059c8fe_caseD_8:
    if (*(int *)((int)param_1 + 4) == 0) {
      return (int)pvVar6;
    }
    *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
    *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
    *(uint *)(*(int *)((int)param_1 + 0x1c) + 8) = (uint)**(byte **)param_1 << 0x18;
    *(int *)param_1 = *(int *)param_1 + 1;
    **(undefined4 **)((int)param_1 + 0x1c) = 9;
    pvVar6 = pvVar5;
  case 9:
    if (*(int *)((int)param_1 + 4) == 0) {
      return (int)pvVar6;
    }
    *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
    *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
    piVar1 = (int *)(*(int *)((int)param_1 + 0x1c) + 8);
    *piVar1 = *piVar1 + (uint)**(byte **)param_1 * 0x10000;
    *(int *)param_1 = *(int *)param_1 + 1;
    **(undefined4 **)((int)param_1 + 0x1c) = 10;
    pvVar6 = pvVar5;
  case 10:
    goto switchD_0059c8fe_caseD_a;
  case 0xb:
    goto switchD_0059c8fe_caseD_b;
  case 0xc:
    goto LAB_0059caf8;
  case 0xd:
    return -3;
  default:
    goto LAB_0059caf8;
  }
LAB_0059cae8:
  puVar4 = *(undefined4 **)((int)param_1 + 0x1c);
  goto LAB_0059caeb;
switchD_0059c8fe_caseD_a:
  if (*(int *)((int)param_1 + 4) == 0) {
    return (int)pvVar6;
  }
  *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
  *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
  piVar1 = (int *)(*(int *)((int)param_1 + 0x1c) + 8);
  *piVar1 = *piVar1 + (uint)**(byte **)param_1 * 0x100;
  *(int *)param_1 = *(int *)param_1 + 1;
  **(undefined4 **)((int)param_1 + 0x1c) = 0xb;
  pvVar6 = pvVar5;
switchD_0059c8fe_caseD_b:
  if (*(int *)((int)param_1 + 4) == 0) {
    return (int)pvVar6;
  }
  *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
  *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
  piVar1 = (int *)(*(int *)((int)param_1 + 0x1c) + 8);
  *piVar1 = *piVar1 + (uint)**(byte **)param_1;
  puVar4 = *(undefined4 **)((int)param_1 + 0x1c);
  *(int *)param_1 = *(int *)param_1 + 1;
  if (puVar4[1] == puVar4[2]) {
    **(undefined4 **)((int)param_1 + 0x1c) = 0xc;
LAB_0059caf8:
    return 1;
  }
  *puVar4 = 0xd;
  *(char **)((int)param_1 + 0x18) = "incorrect data check";
LAB_0059cade:
  *(undefined4 *)(*(int *)((int)param_1 + 0x1c) + 4) = 5;
  pvVar6 = pvVar5;
  goto LAB_0059cae8;
switchD_0059c8fe_caseD_3:
  if (*(int *)((int)param_1 + 4) == 0) {
    return (int)pvVar6;
  }
  *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
  *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
  piVar1 = (int *)(*(int *)((int)param_1 + 0x1c) + 8);
  *piVar1 = *piVar1 + (uint)**(byte **)param_1 * 0x10000;
  *(int *)param_1 = *(int *)param_1 + 1;
  **(undefined4 **)((int)param_1 + 0x1c) = 4;
  pvVar6 = pvVar5;
switchD_0059c8fe_caseD_4:
  if (*(int *)((int)param_1 + 4) == 0) {
    return (int)pvVar6;
  }
  *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
  *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
  piVar1 = (int *)(*(int *)((int)param_1 + 0x1c) + 8);
  *piVar1 = *piVar1 + (uint)**(byte **)param_1 * 0x100;
  *(int *)param_1 = *(int *)param_1 + 1;
  **(undefined4 **)((int)param_1 + 0x1c) = 5;
  pvVar6 = pvVar5;
switchD_0059c8fe_caseD_5:
  if (*(int *)((int)param_1 + 4) != 0) {
    *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + 1;
    *(int *)((int)param_1 + 4) = *(int *)((int)param_1 + 4) + -1;
    piVar1 = (int *)(*(int *)((int)param_1 + 0x1c) + 8);
    *piVar1 = *piVar1 + (uint)**(byte **)param_1;
    *(int *)param_1 = *(int *)param_1 + 1;
    *(undefined4 *)((int)param_1 + 0x30) = (*(undefined4 **)((int)param_1 + 0x1c))[2];
    **(undefined4 **)((int)param_1 + 0x1c) = 6;
    return 2;
  }
  return (int)pvVar6;
}

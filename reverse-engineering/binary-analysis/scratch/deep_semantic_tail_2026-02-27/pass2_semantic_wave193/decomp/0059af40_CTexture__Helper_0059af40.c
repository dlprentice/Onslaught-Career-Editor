/* address: 0x0059af40 */
/* name: CTexture__Helper_0059af40 */
/* signature: void __stdcall CTexture__Helper_0059af40(void * param_1) */


void CTexture__Helper_0059af40(void *param_1)

{
  undefined4 *puVar1;
  uint uVar2;
  void *pvVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int *extraout_ECX;
  int *piVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int *piVar11;

  pvVar3 = param_1;
  iVar4 = *(int *)((int)param_1 + 0x14);
  if (iVar4 != 0xca) {
    puVar1 = *(undefined4 **)param_1;
    puVar1[5] = 0x14;
    puVar1[6] = iVar4;
    (*(code *)*puVar1)(param_1);
  }
  iVar4 = *(int *)((int)param_1 + 0x30);
  uVar2 = *(uint *)((int)param_1 + 0x34);
  if ((uint)(iVar4 * 8) < uVar2 || iVar4 * 8 - uVar2 == 0) {
    iVar4 = CDXTexture__CeilDiv(*(int *)((int)param_1 + 0x1c),8);
    *(int *)((int)param_1 + 0x70) = iVar4;
    iVar4 = CDXTexture__CeilDiv(*(int *)((int)param_1 + 0x20),8);
    *(undefined4 *)((int)param_1 + 0x140) = 1;
  }
  else if ((uint)(iVar4 * 4) < uVar2 || iVar4 * 4 - uVar2 == 0) {
    iVar4 = CDXTexture__CeilDiv(*(int *)((int)param_1 + 0x1c),4);
    *(int *)((int)param_1 + 0x70) = iVar4;
    iVar4 = CDXTexture__CeilDiv(*(int *)((int)param_1 + 0x20),4);
    *(undefined4 *)((int)param_1 + 0x140) = 2;
  }
  else if (uVar2 < (uint)(iVar4 * 2)) {
    iVar4 = *(int *)((int)param_1 + 0x20);
    *(undefined4 *)((int)param_1 + 0x70) = *(undefined4 *)((int)param_1 + 0x1c);
    *(undefined4 *)((int)param_1 + 0x140) = 8;
  }
  else {
    iVar4 = CDXTexture__CeilDiv(*(int *)((int)param_1 + 0x1c),2);
    *(int *)((int)param_1 + 0x70) = iVar4;
    iVar4 = CDXTexture__CeilDiv(*(int *)((int)param_1 + 0x20),2);
    *(undefined4 *)((int)param_1 + 0x140) = 4;
  }
  piVar7 = *(int **)((int)param_1 + 0xdc);
  *(int *)((int)param_1 + 0x74) = iVar4;
  if (0 < (int)*(void **)((int)param_1 + 0x24)) {
    iVar4 = *(int *)((int)param_1 + 0x140);
    piVar7 = piVar7 + 3;
    param_1 = *(void **)((int)param_1 + 0x24);
    do {
      iVar5 = iVar4;
      if (iVar4 < 8) {
        iVar8 = *(int *)((int)pvVar3 + 0x138) * iVar4;
        do {
          iVar9 = piVar7[-1] * iVar5 * 2;
          if ((iVar9 - iVar8 != 0 && iVar8 <= iVar9) ||
             (iVar9 = *(int *)((int)pvVar3 + 0x13c) * iVar4, iVar10 = *piVar7 * iVar5 * 2,
             iVar10 - iVar9 != 0 && iVar9 <= iVar10)) break;
          iVar5 = iVar5 * 2;
        } while (iVar5 < 8);
      }
      piVar7[6] = iVar5;
      piVar7 = piVar7 + 0x15;
      param_1 = (void *)((int)param_1 + -1);
    } while (param_1 != (void *)0x0);
  }
  iVar4 = 0;
  if (0 < *(int *)((int)pvVar3 + 0x24)) {
    piVar11 = (int *)(*(int *)((int)pvVar3 + 0xdc) + 0x24);
    do {
      iVar8 = CDXTexture__CeilDiv(piVar11[-7] * *piVar11 * *(int *)((int)pvVar3 + 0x1c),
                                  *(int *)((int)pvVar3 + 0x138) << 3);
      iVar5 = *(int *)((int)pvVar3 + 0x13c);
      piVar11[1] = iVar8;
      iVar5 = CDXTexture__CeilDiv(piVar11[-6] * *(int *)((int)pvVar3 + 0x20) * *piVar11,iVar5 << 3);
      piVar11[2] = iVar5;
      iVar4 = iVar4 + 1;
      piVar11 = piVar11 + 0x15;
      piVar7 = extraout_ECX;
    } while (iVar4 < *(int *)((int)pvVar3 + 0x24));
  }
  switch(*(undefined4 *)((int)pvVar3 + 0x2c)) {
  case 1:
    *(undefined4 *)((int)pvVar3 + 0x78) = 1;
    break;
  case 2:
  case 3:
    *(undefined4 *)((int)pvVar3 + 0x78) = 3;
    break;
  case 4:
  case 5:
    *(undefined4 *)((int)pvVar3 + 0x78) = 4;
    break;
  default:
    piVar7 = *(int **)((int)pvVar3 + 0x24);
    *(int **)((int)pvVar3 + 0x78) = piVar7;
  }
  uVar6 = 1;
  if (*(int *)((int)pvVar3 + 0x54) == 0) {
    uVar6 = *(undefined4 *)((int)pvVar3 + 0x78);
  }
  *(undefined4 *)((int)pvVar3 + 0x7c) = uVar6;
  iVar4 = CTexture__Helper_0059aec0((int)piVar7,(int)pvVar3);
  if (iVar4 == 0) {
    *(undefined4 *)((int)pvVar3 + 0x80) = 1;
    return;
  }
  *(undefined4 *)((int)pvVar3 + 0x80) = *(undefined4 *)((int)pvVar3 + 0x13c);
  return;
}

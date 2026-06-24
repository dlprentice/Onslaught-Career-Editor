/* address: 0x00591720 */
/* name: CFastVB__Unk_00591720 */
/* signature: int CFastVB__Unk_00591720(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Unk_00591720(void)

{
  byte bVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  int unaff_EBX;
  byte *pbVar10;
  byte *pbVar11;
  int *unaff_ESI;
  uint *puVar12;
  undefined4 *puVar13;
  int *piStack_18;
  int iStack_10;

  puVar13 = (undefined4 *)unaff_ESI[6];
  pbVar10 = (byte *)*puVar13;
  iVar4 = puVar13[1];
  if (*(int *)(unaff_ESI[0x6f] + 0x10) == 0) {
    puVar6 = (undefined4 *)*unaff_ESI;
    puVar6[5] = 0x3e;
    (*(code *)*puVar6)();
  }
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar13[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iVar4 = puVar13[1];
    pbVar10 = (byte *)*puVar13;
  }
  bVar1 = *pbVar10;
  iVar4 = iVar4 + -1;
  pbVar10 = pbVar10 + 1;
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar13[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iVar4 = puVar13[1];
    pbVar10 = (byte *)*puVar13;
  }
  uVar9 = (uint)bVar1 * 0x100 + (uint)*pbVar10;
  iVar4 = iVar4 + -1;
  pbVar10 = pbVar10 + 1;
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar13[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iVar4 = puVar13[1];
    pbVar10 = (byte *)*puVar13;
  }
  puVar6 = (undefined4 *)(uint)*pbVar10;
  iVar5 = *unaff_ESI;
  *(undefined4 *)(iVar5 + 0x14) = 0x67;
  iVar4 = iVar4 + -1;
  pbVar10 = pbVar10 + 1;
  *(undefined4 **)(iVar5 + 0x18) = puVar6;
  (**(code **)(iVar5 + 4))();
  if (((unaff_EBX != uVar9 * 2 + 6) || (uVar9 == 0)) || (4 < uVar9)) {
    puVar2 = (undefined4 *)*unaff_ESI;
    puVar2[5] = 0xb;
    (*(code *)*puVar2)();
  }
  unaff_ESI[0x53] = uVar9;
  iStack_10 = 0;
  if (uVar9 != 0) {
    piStack_18 = unaff_ESI + 0x54;
    do {
      if (iVar4 == 0) {
        iVar4 = (*(code *)puVar13[3])();
        if (iVar4 == 0) {
          return 0;
        }
        iVar4 = puVar13[1];
        pbVar10 = (byte *)*puVar13;
      }
      uVar7 = (uint)*pbVar10;
      iVar4 = iVar4 + -1;
      pbVar10 = pbVar10 + 1;
      if (iVar4 == 0) {
        iVar4 = (*(code *)puVar13[3])();
        if (iVar4 == 0) {
          return 0;
        }
        iVar4 = puVar13[1];
        pbVar10 = (byte *)*puVar13;
      }
      puVar12 = (uint *)unaff_ESI[0x37];
      iVar4 = iVar4 + -1;
      bVar1 = *pbVar10;
      pbVar10 = pbVar10 + 1;
      iVar5 = 0;
      if (0 < unaff_ESI[9]) {
        do {
          if (uVar7 == *puVar12) goto LAB_0059189d;
          iVar5 = iVar5 + 1;
          puVar12 = puVar12 + 0x15;
        } while (iVar5 < unaff_ESI[9]);
      }
      puVar13 = (undefined4 *)*unaff_ESI;
      puVar13[5] = 5;
      puVar13[6] = uVar7;
      (*(code *)*puVar13)();
LAB_0059189d:
      puVar12[5] = (int)(uint)bVar1 >> 4;
      *piStack_18 = (int)puVar12;
      iVar5 = *unaff_ESI;
      puVar12[6] = bVar1 & 0xf;
      *(uint *)(iVar5 + 0x18) = uVar7;
      *(uint *)(iVar5 + 0x1c) = puVar12[5];
      *(uint *)(iVar5 + 0x20) = puVar12[6];
      *(undefined4 *)(iVar5 + 0x14) = 0x68;
      (**(code **)(iVar5 + 4))();
      iStack_10 = iStack_10 + 1;
      piStack_18 = piStack_18 + 1;
      puVar13 = puVar6;
    } while (iStack_10 < (int)uVar9);
  }
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar13[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iVar4 = puVar13[1];
    pbVar10 = (byte *)*puVar13;
  }
  iVar4 = iVar4 + -1;
  pbVar11 = pbVar10 + 1;
  unaff_ESI[0x65] = (uint)*pbVar10;
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar13[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iVar4 = puVar13[1];
    pbVar11 = (byte *)*puVar13;
  }
  iVar4 = iVar4 + -1;
  pbVar10 = pbVar11 + 1;
  unaff_ESI[0x66] = (uint)*pbVar11;
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar13[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iVar4 = puVar13[1];
    pbVar10 = (byte *)*puVar13;
  }
  uVar9 = *pbVar10 & 0xf;
  iVar8 = (int)(uint)*pbVar10 >> 4;
  unaff_ESI[0x68] = uVar9;
  iVar5 = *unaff_ESI;
  *(int *)(iVar5 + 0x18) = unaff_ESI[0x65];
  iVar3 = unaff_ESI[0x66];
  *(int *)(iVar5 + 0x20) = iVar8;
  unaff_ESI[0x67] = iVar8;
  *(int *)(iVar5 + 0x1c) = iVar3;
  *(uint *)(iVar5 + 0x24) = uVar9;
  *(undefined4 *)(iVar5 + 0x14) = 0x69;
  (**(code **)(iVar5 + 4))();
  iVar5 = unaff_ESI[0x25];
  *(undefined4 *)(unaff_ESI[0x6f] + 0x14) = 0;
  *puVar13 = pbVar10 + 1;
  puVar13[1] = iVar4 + -1;
  unaff_ESI[0x25] = iVar5 + 1;
  return 1;
}

/* address: 0x00591460 */
/* name: CDXTexture__DecodeJpegSegment_StartOfFrame */
/* signature: int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int param_1) */


int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int param_1)

{
  byte bVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int in_EAX;
  int iVar6;
  undefined4 *unaff_EBX;
  int iVar7;
  int unaff_EBP;
  uint *puVar8;
  int *unaff_ESI;
  byte *pbVar9;
  byte *pbVar10;
  uint uVar11;

  piVar2 = (int *)unaff_ESI[6];
  iVar7 = piVar2[1];
  iVar6 = *piVar2;
  unaff_ESI[0x38] = in_EAX;
  unaff_ESI[0x39] = param_1;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    iVar6 = *piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  iVar6 = iVar6 + 1;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    iVar6 = *piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  pbVar9 = (byte *)(iVar6 + 1);
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    pbVar9 = (byte *)*piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  pbVar10 = pbVar9 + 1;
  unaff_ESI[0x36] = (uint)*pbVar9;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    pbVar10 = (byte *)*piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  pbVar9 = pbVar10 + 1;
  unaff_ESI[8] = (uint)*pbVar10 << 8;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    pbVar9 = (byte *)*piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  pbVar10 = pbVar9 + 1;
  unaff_ESI[8] = unaff_ESI[8] + (uint)*pbVar9;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    pbVar10 = (byte *)*piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  pbVar9 = pbVar10 + 1;
  unaff_ESI[7] = (uint)*pbVar10 << 8;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    pbVar9 = (byte *)*piVar2;
    iVar7 = piVar2[1];
  }
  iVar7 = iVar7 + -1;
  pbVar10 = pbVar9 + 1;
  unaff_ESI[7] = unaff_ESI[7] + (uint)*pbVar9;
  if (iVar7 == 0) {
    iVar6 = (*(code *)piVar2[3])();
    if (iVar6 == 0) {
      return 0;
    }
    pbVar10 = (byte *)*piVar2;
    iVar7 = piVar2[1];
  }
  iVar6 = unaff_ESI[7];
  unaff_ESI[9] = (uint)*pbVar10;
  iVar3 = *unaff_ESI;
  *(int *)(iVar3 + 0x18) = unaff_ESI[0x69];
  iVar4 = unaff_ESI[8];
  *(int *)(iVar3 + 0x1c) = iVar6;
  iVar6 = unaff_ESI[9];
  *(int *)(iVar3 + 0x20) = iVar4;
  *(int *)(iVar3 + 0x24) = iVar6;
  iVar7 = iVar7 + -1;
  pbVar10 = pbVar10 + 1;
  *(undefined4 *)(iVar3 + 0x14) = 100;
  (**(code **)(iVar3 + 4))();
  if (*(int *)(unaff_ESI[0x6f] + 0x10) != 0) {
    puVar5 = (undefined4 *)*unaff_ESI;
    puVar5[5] = 0x3a;
    (*(code *)*puVar5)();
  }
  if (((unaff_ESI[8] == 0) || (unaff_ESI[7] == 0)) || (unaff_ESI[9] < 1)) {
    puVar5 = (undefined4 *)*unaff_ESI;
    puVar5[5] = 0x20;
    (*(code *)*puVar5)();
  }
  if (unaff_EBP != unaff_ESI[9] * 3) {
    puVar5 = (undefined4 *)*unaff_ESI;
    puVar5[5] = 0xb;
    (*(code *)*puVar5)();
  }
  if (unaff_ESI[0x37] == 0) {
    iVar6 = (**(code **)unaff_ESI[1])();
    unaff_ESI[0x37] = iVar6;
  }
  puVar8 = (uint *)unaff_ESI[0x37];
  uVar11 = 0;
  if (0 < unaff_ESI[9]) {
    do {
      puVar8[1] = uVar11;
      if (iVar7 == 0) {
        iVar6 = (*(code *)unaff_EBX[3])();
        if (iVar6 == 0) {
          return 0;
        }
        pbVar10 = (byte *)*unaff_EBX;
        iVar7 = unaff_EBX[1];
      }
      iVar7 = iVar7 + -1;
      pbVar9 = pbVar10 + 1;
      *puVar8 = (uint)*pbVar10;
      if (iVar7 == 0) {
        iVar6 = (*(code *)unaff_EBX[3])();
        if (iVar6 == 0) {
          return 0;
        }
        pbVar9 = (byte *)*unaff_EBX;
        iVar7 = unaff_EBX[1];
      }
      bVar1 = *pbVar9;
      iVar7 = iVar7 + -1;
      pbVar9 = pbVar9 + 1;
      puVar8[2] = (int)(uint)bVar1 >> 4;
      puVar8[3] = bVar1 & 0xf;
      if (iVar7 == 0) {
        iVar6 = (*(code *)unaff_EBX[3])();
        if (iVar6 == 0) {
          return 0;
        }
        pbVar9 = (byte *)*unaff_EBX;
        iVar7 = unaff_EBX[1];
      }
      iVar6 = *unaff_ESI;
      puVar8[4] = (uint)*pbVar9;
      *(uint *)(iVar6 + 0x18) = *puVar8;
      *(uint *)(iVar6 + 0x1c) = puVar8[2];
      *(uint *)(iVar6 + 0x20) = puVar8[3];
      *(uint *)(iVar6 + 0x24) = puVar8[4];
      iVar7 = iVar7 + -1;
      pbVar10 = pbVar9 + 1;
      *(undefined4 *)(iVar6 + 0x14) = 0x65;
      (**(code **)(iVar6 + 4))();
      uVar11 = uVar11 + 1;
      puVar8 = puVar8 + 0x15;
    } while ((int)uVar11 < unaff_ESI[9]);
  }
  *(undefined4 *)(unaff_ESI[0x6f] + 0x10) = 1;
  *unaff_EBX = pbVar10;
  unaff_EBX[1] = iVar7;
  return 1;
}

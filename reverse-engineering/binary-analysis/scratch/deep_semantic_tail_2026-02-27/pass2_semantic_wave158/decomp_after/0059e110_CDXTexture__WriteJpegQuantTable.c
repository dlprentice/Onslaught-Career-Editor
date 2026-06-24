/* address: 0x0059e110 */
/* name: CDXTexture__WriteJpegQuantTable */
/* signature: char __stdcall CDXTexture__WriteJpegQuantTable(int param_1) */


char CDXTexture__WriteJpegQuantTable(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined1 *puVar4;
  int *piVar5;
  char *pcVar6;
  int *piVar7;
  bool bVar8;
  ushort *puVar9;
  int iVar10;
  int *unaff_ESI;
  int *piVar11;

  iVar2 = unaff_ESI[param_1 + 0x12];
  if (iVar2 == 0) {
    puVar3 = (undefined4 *)*unaff_ESI;
    puVar3[5] = 0x34;
    puVar3[6] = param_1;
    (*(code *)*puVar3)();
  }
  bVar8 = false;
  puVar9 = (ushort *)(iVar2 + 4);
  iVar10 = 8;
  do {
    if (0xff < puVar9[-2]) {
      bVar8 = true;
    }
    if (0xff < puVar9[-1]) {
      bVar8 = true;
    }
    if (0xff < *puVar9) {
      bVar8 = true;
    }
    if (0xff < puVar9[1]) {
      bVar8 = true;
    }
    if (0xff < puVar9[2]) {
      bVar8 = true;
    }
    if (0xff < puVar9[3]) {
      bVar8 = true;
    }
    if (0xff < puVar9[4]) {
      bVar8 = true;
    }
    if (0xff < puVar9[5]) {
      bVar8 = true;
    }
    puVar9 = puVar9 + 8;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  if (*(int *)(iVar2 + 0x80) == 0) {
    puVar3 = (undefined4 *)unaff_ESI[6];
    puVar4 = (undefined1 *)*puVar3;
    *puVar4 = 0xff;
    *puVar3 = puVar4 + 1;
    iVar10 = puVar3[1];
    puVar3[1] = iVar10 + -1;
    if (iVar10 + -1 == 0) {
      iVar10 = (*(code *)puVar3[3])();
      if (iVar10 == 0) {
        puVar3 = (undefined4 *)*unaff_ESI;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)();
      }
    }
    puVar3 = (undefined4 *)unaff_ESI[6];
    puVar4 = (undefined1 *)*puVar3;
    *puVar4 = 0xdb;
    *puVar3 = puVar4 + 1;
    piVar11 = puVar3 + 1;
    *piVar11 = *piVar11 + -1;
    if (*piVar11 == 0) {
      iVar10 = (*(code *)puVar3[3])();
      if (iVar10 == 0) {
        puVar3 = (undefined4 *)*unaff_ESI;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)();
      }
    }
    puVar3 = (undefined4 *)unaff_ESI[6];
    puVar4 = (undefined1 *)*puVar3;
    *puVar4 = 0;
    iVar10 = puVar3[1];
    *puVar3 = puVar4 + 1;
    puVar3[1] = iVar10 + -1;
    if (iVar10 + -1 == 0) {
      iVar10 = (*(code *)puVar3[3])();
      if (iVar10 == 0) {
        puVar3 = (undefined4 *)*unaff_ESI;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)();
      }
    }
    piVar5 = (int *)unaff_ESI[6];
    pcVar6 = (char *)*piVar5;
    *pcVar6 = (-bVar8 & 0x40U) + 0x43;
    *piVar5 = (int)(pcVar6 + 1);
    piVar11 = piVar5 + 1;
    *piVar11 = *piVar11 + -1;
    if (*piVar11 == 0) {
      iVar10 = (*(code *)piVar5[3])();
      if (iVar10 == 0) {
        puVar3 = (undefined4 *)*unaff_ESI;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)();
      }
    }
    piVar5 = (int *)unaff_ESI[6];
    pcVar6 = (char *)*piVar5;
    *pcVar6 = bVar8 * '\x10' + (char)param_1;
    *piVar5 = (int)(pcVar6 + 1);
    piVar11 = piVar5 + 1;
    *piVar11 = *piVar11 + -1;
    if (*piVar11 == 0) {
      iVar10 = (*(code *)piVar5[3])();
      if (iVar10 == 0) {
        puVar3 = (undefined4 *)*unaff_ESI;
        puVar3[5] = 0x18;
        (*(code *)*puVar3)();
      }
    }
    piVar11 = &DAT_005f37f8;
    do {
      uVar1 = *(undefined2 *)(iVar2 + *piVar11 * 2);
      if (bVar8) {
        piVar7 = (int *)unaff_ESI[6];
        puVar4 = (undefined1 *)*piVar7;
        *puVar4 = (char)((ushort)uVar1 >> 8);
        *piVar7 = (int)(puVar4 + 1);
        piVar5 = piVar7 + 1;
        *piVar5 = *piVar5 + -1;
        if (*piVar5 == 0) {
          iVar10 = (*(code *)piVar7[3])();
          if (iVar10 == 0) {
            puVar3 = (undefined4 *)*unaff_ESI;
            puVar3[5] = 0x18;
            (*(code *)*puVar3)();
          }
        }
      }
      piVar7 = (int *)unaff_ESI[6];
      puVar4 = (undefined1 *)*piVar7;
      *puVar4 = (char)uVar1;
      *piVar7 = (int)(puVar4 + 1);
      piVar5 = piVar7 + 1;
      *piVar5 = *piVar5 + -1;
      if (*piVar5 == 0) {
        iVar10 = (*(code *)piVar7[3])();
        if (iVar10 == 0) {
          puVar3 = (undefined4 *)*unaff_ESI;
          puVar3[5] = 0x18;
          (*(code *)*puVar3)();
        }
      }
      piVar11 = piVar11 + 1;
    } while ((int)piVar11 < 0x5f38f8);
    *(undefined4 *)(iVar2 + 0x80) = 1;
  }
  return bVar8;
}

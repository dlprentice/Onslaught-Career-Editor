/* address: 0x005b7920 */
/* name: CDXTexture__Unk_005b7920 */
/* signature: void CDXTexture__Unk_005b7920(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_005b7920(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  int *unaff_ESI;
  int *piVar9;
  bool bVar10;
  int *piStack_a40;
  int iStack_a3c;
  int local_a28 [10];
  int aiStack_a00 [640];

  if (unaff_ESI[0x2a] < 1) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x13;
    puVar1[6] = 0;
    (*(code *)*puVar1)();
  }
  piVar7 = (int *)unaff_ESI[0x2b];
  if ((piVar7[5] == 0) && (piVar7[6] == 0x3f)) {
    iVar6 = unaff_ESI[0xf];
    unaff_ESI[0x3b] = 0;
    if (iVar6 < 1) goto LAB_005b7995;
    iVar5 = 0;
    piVar9 = local_a28;
  }
  else {
    unaff_ESI[0x3b] = 1;
    if (unaff_ESI[0xf] < 1) goto LAB_005b7995;
    iVar6 = (unaff_ESI[0xf] & 0xffffffU) << 6;
    iVar5 = -1;
    piVar9 = aiStack_a00;
  }
  for (; iVar6 != 0; iVar6 = iVar6 + -1) {
    *piVar9 = iVar5;
    piVar9 = piVar9 + 1;
  }
LAB_005b7995:
  iStack_a3c = 1;
  if (0 < unaff_ESI[0x2a]) {
    do {
      iVar5 = iStack_a3c;
      iVar6 = *piVar7;
      if ((iVar6 < 1) || (4 < iVar6)) {
        puVar1 = (undefined4 *)*unaff_ESI;
        puVar1[5] = 0x1a;
        puVar1[6] = iVar6;
        puVar1[7] = 4;
        (*(code *)*puVar1)();
      }
      iVar8 = 0;
      if (0 < iVar6) {
        do {
          iVar2 = piVar7[iVar8 + 1];
          if ((iVar2 < 0) || (unaff_ESI[0xf] <= iVar2)) {
            puVar1 = (undefined4 *)*unaff_ESI;
            puVar1[5] = 0x13;
            puVar1[6] = iStack_a3c;
            (*(code *)*puVar1)();
          }
          if ((0 < iVar8) && (iVar2 <= piVar7[iVar8])) {
            puVar1 = (undefined4 *)*unaff_ESI;
            puVar1[5] = 0x13;
            puVar1[6] = iStack_a3c;
            (*(code *)*puVar1)();
          }
          iVar8 = iVar8 + 1;
        } while (iVar8 < iVar6);
      }
      iVar8 = piVar7[5];
      iVar2 = piVar7[6];
      iVar3 = piVar7[7];
      iVar4 = piVar7[8];
      if (unaff_ESI[0x3b] == 0) {
        if ((((iVar8 != 0) || (iVar2 != 0x3f)) || (iVar3 != 0)) || (iVar4 != 0)) {
          puVar1 = (undefined4 *)*unaff_ESI;
          puVar1[5] = 0x11;
          puVar1[6] = iStack_a3c;
          (*(code *)*puVar1)();
        }
        piVar9 = piVar7;
        if (0 < iVar6) {
          do {
            iVar8 = piVar9[1];
            if (local_a28[iVar8] != 0) {
              puVar1 = (undefined4 *)*unaff_ESI;
              puVar1[5] = 0x13;
              puVar1[6] = iStack_a3c;
              (*(code *)*puVar1)();
            }
            iVar6 = iVar6 + -1;
            local_a28[iVar8] = 1;
            piVar9 = piVar9 + 1;
          } while (iVar6 != 0);
        }
      }
      else {
        if (((((iVar8 < 0) || (0x3f < iVar8)) ||
             ((iVar2 < iVar8 || ((0x3f < iVar2 || (iVar3 < 0)))))) || (10 < iVar3)) ||
           ((iVar4 < 0 || (10 < iVar4)))) {
          puVar1 = (undefined4 *)*unaff_ESI;
          puVar1[5] = 0x11;
          puVar1[6] = iStack_a3c;
          (*(code *)*puVar1)();
        }
        if (iVar8 == 0) {
          bVar10 = iVar2 == 0;
        }
        else {
          bVar10 = iVar6 == 1;
        }
        if (!bVar10) {
          puVar1 = (undefined4 *)*unaff_ESI;
          puVar1[5] = 0x11;
          puVar1[6] = iStack_a3c;
          (*(code *)*puVar1)();
        }
        iStack_a3c = iVar6;
        piStack_a40 = piVar7;
        if (0 < iVar6) {
          do {
            piStack_a40 = piStack_a40 + 1;
            piVar9 = aiStack_a00 + *piStack_a40 * 0x40;
            iVar6 = iVar8;
            if ((iVar8 != 0) && (*piVar9 < 0)) {
              puVar1 = (undefined4 *)*unaff_ESI;
              puVar1[5] = 0x11;
              puVar1[6] = iVar5;
              (*(code *)*puVar1)();
            }
            for (; iVar6 <= iVar2; iVar6 = iVar6 + 1) {
              if (piVar9[iVar6] < 0) {
                bVar10 = iVar3 == 0;
LAB_005b7b26:
                if (!bVar10) goto LAB_005b7b28;
              }
              else {
                if (iVar3 == piVar9[iVar6]) {
                  bVar10 = iVar4 == iVar3 + -1;
                  goto LAB_005b7b26;
                }
LAB_005b7b28:
                puVar1 = (undefined4 *)*unaff_ESI;
                puVar1[5] = 0x11;
                puVar1[6] = iVar5;
                (*(code *)*puVar1)();
              }
              piVar9[iVar6] = iVar4;
            }
            iStack_a3c = iStack_a3c + -1;
          } while (iStack_a3c != 0);
        }
      }
      piVar7 = piVar7 + 9;
      iStack_a3c = iVar5 + 1;
    } while (iStack_a3c <= unaff_ESI[0x2a]);
  }
  iVar6 = 0;
  if (unaff_ESI[0x3b] == 0) {
    if (0 < unaff_ESI[0xf]) {
      do {
        if (local_a28[iVar6] == 0) {
          puVar1 = (undefined4 *)*unaff_ESI;
          puVar1[5] = 0x2d;
          (*(code *)*puVar1)();
        }
        iVar6 = iVar6 + 1;
      } while (iVar6 < unaff_ESI[0xf]);
    }
  }
  else if (0 < unaff_ESI[0xf]) {
    piVar7 = aiStack_a00;
    do {
      if (*piVar7 < 0) {
        puVar1 = (undefined4 *)*unaff_ESI;
        puVar1[5] = 0x2d;
        (*(code *)*puVar1)();
      }
      iVar6 = iVar6 + 1;
      piVar7 = piVar7 + 0x40;
    } while (iVar6 < unaff_ESI[0xf]);
    return;
  }
  return;
}

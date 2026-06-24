/* address: 0x0059e770 */
/* name: CDXTexture__Unk_0059e770 */
/* signature: void CDXTexture__Unk_0059e770(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_0059e770(void)

{
  undefined4 *puVar1;
  undefined1 *puVar2;
  int *piVar3;
  undefined1 *puVar4;
  char *pcVar5;
  char cVar6;
  int iVar7;
  int iVar8;
  char cVar9;
  char cVar10;
  int *piVar11;
  int *unaff_ESI;

  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = 0xff;
  *puVar1 = puVar2 + 1;
  iVar7 = puVar1[1];
  puVar1[1] = iVar7 + -1;
  if ((iVar7 + -1 == 0) && (iVar7 = (*(code *)puVar1[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = 0xda;
  *puVar1 = puVar2 + 1;
  piVar11 = puVar1 + 1;
  *piVar11 = *piVar11 + -1;
  if ((*piVar11 == 0) && (iVar7 = (*(code *)puVar1[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  piVar3 = (int *)unaff_ESI[6];
  puVar2 = (undefined1 *)*piVar3;
  iVar7 = unaff_ESI[0x3f] * 2 + 6;
  *puVar2 = (char)((uint)iVar7 >> 8);
  *piVar3 = (int)(puVar2 + 1);
  piVar11 = piVar3 + 1;
  *piVar11 = *piVar11 + -1;
  if ((*piVar11 == 0) && (iVar8 = (*(code *)piVar3[3])(), iVar8 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  piVar3 = (int *)unaff_ESI[6];
  puVar2 = (undefined1 *)*piVar3;
  *puVar2 = (char)iVar7;
  *piVar3 = (int)(puVar2 + 1);
  piVar11 = piVar3 + 1;
  *piVar11 = *piVar11 + -1;
  if ((*piVar11 == 0) && (iVar7 = (*(code *)piVar3[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = (char)unaff_ESI[0x3f];
  *puVar1 = puVar2 + 1;
  piVar11 = puVar1 + 1;
  *piVar11 = *piVar11 + -1;
  if ((*piVar11 == 0) && (iVar7 = (*(code *)puVar1[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  iVar7 = 0;
  if (0 < unaff_ESI[0x3f]) {
    piVar11 = unaff_ESI + 0x40;
    do {
      puVar1 = (undefined4 *)unaff_ESI[6];
      puVar2 = (undefined1 *)*piVar11;
      puVar4 = (undefined1 *)*puVar1;
      *puVar4 = *puVar2;
      *puVar1 = puVar4 + 1;
      piVar3 = puVar1 + 1;
      *piVar3 = *piVar3 + -1;
      if ((*piVar3 == 0) && (iVar8 = (*(code *)puVar1[3])(), iVar8 == 0)) {
        puVar1 = (undefined4 *)*unaff_ESI;
        puVar1[5] = 0x18;
        (*(code *)*puVar1)();
      }
      cVar9 = (char)*(undefined4 *)(puVar2 + 0x14);
      cVar10 = (char)*(undefined4 *)(puVar2 + 0x18);
      if (unaff_ESI[0x3b] != 0) {
        cVar6 = cVar10;
        if (unaff_ESI[0x51] == 0) {
          cVar10 = '\0';
          if ((unaff_ESI[0x53] == 0) || (cVar6 = '\0', unaff_ESI[0x2d] != 0)) goto LAB_0059e8aa;
        }
        cVar10 = cVar6;
        cVar9 = '\0';
      }
LAB_0059e8aa:
      piVar3 = (int *)unaff_ESI[6];
      pcVar5 = (char *)*piVar3;
      *pcVar5 = cVar9 * '\x10' + cVar10;
      iVar8 = piVar3[1];
      *piVar3 = (int)(pcVar5 + 1);
      piVar3[1] = iVar8 + -1;
      if ((iVar8 + -1 == 0) && (iVar8 = (*(code *)piVar3[3])(), iVar8 == 0)) {
        puVar1 = (undefined4 *)*unaff_ESI;
        puVar1[5] = 0x18;
        (*(code *)*puVar1)();
      }
      iVar7 = iVar7 + 1;
      piVar11 = piVar11 + 1;
    } while (iVar7 < unaff_ESI[0x3f]);
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = (char)unaff_ESI[0x51];
  *puVar1 = puVar2 + 1;
  piVar11 = puVar1 + 1;
  *piVar11 = *piVar11 + -1;
  if ((*piVar11 == 0) && (iVar7 = (*(code *)puVar1[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  puVar1 = (undefined4 *)unaff_ESI[6];
  puVar2 = (undefined1 *)*puVar1;
  *puVar2 = (char)unaff_ESI[0x52];
  *puVar1 = puVar2 + 1;
  piVar11 = puVar1 + 1;
  *piVar11 = *piVar11 + -1;
  if ((*piVar11 == 0) && (iVar7 = (*(code *)puVar1[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  piVar11 = (int *)unaff_ESI[6];
  pcVar5 = (char *)*piVar11;
  *pcVar5 = (char)unaff_ESI[0x53] * '\x10' + (char)unaff_ESI[0x54];
  *piVar11 = (int)(pcVar5 + 1);
  iVar7 = piVar11[1];
  piVar11[1] = iVar7 + -1;
  if ((iVar7 + -1 == 0) && (iVar7 = (*(code *)piVar11[3])(), iVar7 == 0)) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x18;
    (*(code *)*puVar1)();
  }
  return;
}

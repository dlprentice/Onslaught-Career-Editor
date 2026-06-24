/* address: 0x005b7c50 */
/* name: CDXTexture__LoadCurrentJpegScanDescriptor */
/* signature: void CDXTexture__LoadCurrentJpegScanDescriptor(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__LoadCurrentJpegScanDescriptor(void)

{
  int iVar1;
  undefined4 *puVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  int *unaff_ESI;

  if (unaff_ESI[0x2b] == 0) {
    iVar7 = unaff_ESI[0xf];
    if (4 < iVar7) {
      puVar2 = (undefined4 *)*unaff_ESI;
      puVar2[5] = 0x1a;
      puVar2[6] = iVar7;
      puVar2[7] = 4;
      (*(code *)*puVar2)();
    }
    iVar7 = 0;
    unaff_ESI[0x3f] = unaff_ESI[0xf];
    if (0 < unaff_ESI[0xf]) {
      iVar6 = 0;
      piVar4 = unaff_ESI + 0x40;
      do {
        *piVar4 = unaff_ESI[0x11] + iVar6;
        iVar7 = iVar7 + 1;
        piVar4 = piVar4 + 1;
        iVar6 = iVar6 + 0x54;
      } while (iVar7 < unaff_ESI[0xf]);
    }
    unaff_ESI[0x51] = 0;
    unaff_ESI[0x53] = 0;
    unaff_ESI[0x54] = 0;
    unaff_ESI[0x52] = 0x3f;
    return;
  }
  piVar4 = (int *)(unaff_ESI[0x2b] + *(int *)(unaff_ESI[0x55] + 0x20) * 0x24);
  iVar7 = *piVar4;
  unaff_ESI[0x3f] = iVar7;
  if (0 < iVar7) {
    piVar5 = unaff_ESI + 0x40;
    piVar3 = piVar4;
    do {
      piVar3 = piVar3 + 1;
      *piVar5 = *piVar3 * 0x54 + unaff_ESI[0x11];
      piVar5 = piVar5 + 1;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
  }
  iVar7 = piVar4[6];
  iVar6 = piVar4[7];
  unaff_ESI[0x51] = piVar4[5];
  iVar1 = piVar4[8];
  unaff_ESI[0x52] = iVar7;
  unaff_ESI[0x53] = iVar6;
  unaff_ESI[0x54] = iVar1;
  return;
}

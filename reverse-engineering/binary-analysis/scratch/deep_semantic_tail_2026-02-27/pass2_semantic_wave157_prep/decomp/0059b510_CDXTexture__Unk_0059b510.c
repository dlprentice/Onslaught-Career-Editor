/* address: 0x0059b510 */
/* name: CDXTexture__Unk_0059b510 */
/* signature: void CDXTexture__Unk_0059b510(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_0059b510(void)

{
  undefined4 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int *unaff_ESI;
  int *piVar6;

  if ((0xffdc < unaff_ESI[8]) || (0xffdc < unaff_ESI[7])) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x29;
    puVar1[6] = 0xffdc;
    (*(code *)*puVar1)();
  }
  iVar5 = unaff_ESI[0x36];
  if (iVar5 != 8) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0xf;
    puVar1[6] = iVar5;
    (*(code *)*puVar1)();
  }
  iVar5 = unaff_ESI[9];
  if (10 < iVar5) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x1a;
    puVar1[6] = iVar5;
    puVar1[7] = 10;
    (*(code *)*puVar1)();
  }
  iVar5 = 0;
  unaff_ESI[0x4e] = 1;
  unaff_ESI[0x4f] = 1;
  if (0 < unaff_ESI[9]) {
    piVar6 = (int *)(unaff_ESI[0x37] + 0xc);
    do {
      if ((((piVar6[-1] < 1) || (4 < piVar6[-1])) || (*piVar6 < 1)) || (4 < *piVar6)) {
        puVar1 = (undefined4 *)*unaff_ESI;
        puVar1[5] = 0x12;
        (*(code *)*puVar1)();
      }
      iVar4 = unaff_ESI[0x4e];
      if (unaff_ESI[0x4e] <= piVar6[-1]) {
        iVar4 = piVar6[-1];
      }
      iVar2 = *piVar6;
      unaff_ESI[0x4e] = iVar4;
      iVar4 = unaff_ESI[0x4f];
      if (unaff_ESI[0x4f] <= iVar2) {
        iVar4 = iVar2;
      }
      unaff_ESI[0x4f] = iVar4;
      iVar5 = iVar5 + 1;
      piVar6 = piVar6 + 0x15;
    } while (iVar5 < unaff_ESI[9]);
  }
  iVar5 = 0;
  unaff_ESI[0x50] = 8;
  if (0 < unaff_ESI[9]) {
    piVar6 = (int *)(unaff_ESI[0x37] + 0x1c);
    do {
      iVar4 = unaff_ESI[7];
      iVar2 = unaff_ESI[0x4e];
      piVar6[2] = 8;
      iVar2 = CDXTexture__Helper_0059c670(piVar6[-5] * iVar4,iVar2 << 3);
      iVar4 = unaff_ESI[0x4f];
      *piVar6 = iVar2;
      iVar3 = CDXTexture__Helper_0059c670(piVar6[-4] * unaff_ESI[8],iVar4 << 3);
      iVar4 = unaff_ESI[7];
      iVar2 = unaff_ESI[0x4e];
      piVar6[1] = iVar3;
      iVar2 = CDXTexture__Helper_0059c670(piVar6[-5] * iVar4,iVar2);
      iVar4 = unaff_ESI[8];
      piVar6[3] = iVar2;
      iVar4 = CDXTexture__Helper_0059c670(piVar6[-4] * iVar4,unaff_ESI[0x4f]);
      piVar6[4] = iVar4;
      iVar4 = unaff_ESI[9];
      piVar6[5] = 1;
      piVar6[0xc] = 0;
      iVar5 = iVar5 + 1;
      piVar6 = piVar6 + 0x15;
    } while (iVar5 < iVar4);
  }
  iVar5 = CDXTexture__Helper_0059c670(unaff_ESI[8],unaff_ESI[0x4f] << 3);
  unaff_ESI[0x51] = iVar5;
  if ((unaff_ESI[9] <= unaff_ESI[0x53]) && (unaff_ESI[0x38] == 0)) {
    *(undefined4 *)(unaff_ESI[0x6e] + 0x10) = 0;
    return;
  }
  *(undefined4 *)(unaff_ESI[0x6e] + 0x10) = 1;
  return;
}

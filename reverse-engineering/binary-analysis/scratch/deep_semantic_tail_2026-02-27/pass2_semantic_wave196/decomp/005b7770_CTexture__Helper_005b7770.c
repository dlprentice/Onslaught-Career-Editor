/* address: 0x005b7770 */
/* name: CTexture__Helper_005b7770 */
/* signature: void CTexture__Helper_005b7770(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__Helper_005b7770(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *unaff_ESI;
  int *piVar5;
  undefined4 *puVar6;

  if ((((unaff_ESI[8] == 0) || (unaff_ESI[7] == 0)) || (unaff_ESI[0xf] < 1)) || (unaff_ESI[9] < 1))
  {
    puVar6 = (undefined4 *)*unaff_ESI;
    puVar6[5] = 0x20;
    (*(code *)*puVar6)();
  }
  if ((0xffdc < unaff_ESI[8]) || (0xffdc < unaff_ESI[7])) {
    puVar6 = (undefined4 *)*unaff_ESI;
    puVar6[5] = 0x29;
    puVar6[6] = 0xffdc;
    (*(code *)*puVar6)();
  }
  iVar4 = unaff_ESI[0xe];
  if (iVar4 != 8) {
    puVar6 = (undefined4 *)*unaff_ESI;
    puVar6[5] = 0xf;
    puVar6[6] = iVar4;
    (*(code *)*puVar6)();
  }
  iVar4 = unaff_ESI[0xf];
  if (10 < iVar4) {
    puVar6 = (undefined4 *)*unaff_ESI;
    puVar6[5] = 0x1a;
    puVar6[6] = iVar4;
    puVar6[7] = 10;
    (*(code *)*puVar6)();
  }
  iVar4 = 0;
  unaff_ESI[0x3c] = 1;
  unaff_ESI[0x3d] = 1;
  if (0 < unaff_ESI[0xf]) {
    piVar5 = (int *)(unaff_ESI[0x11] + 0xc);
    do {
      if (((piVar5[-1] < 1) || (4 < piVar5[-1])) || ((*piVar5 < 1 || (4 < *piVar5)))) {
        puVar6 = (undefined4 *)*unaff_ESI;
        puVar6[5] = 0x12;
        (*(code *)*puVar6)();
      }
      iVar3 = unaff_ESI[0x3c];
      if (unaff_ESI[0x3c] <= piVar5[-1]) {
        iVar3 = piVar5[-1];
      }
      iVar1 = *piVar5;
      unaff_ESI[0x3c] = iVar3;
      iVar3 = unaff_ESI[0x3d];
      if (unaff_ESI[0x3d] <= iVar1) {
        iVar3 = iVar1;
      }
      unaff_ESI[0x3d] = iVar3;
      iVar4 = iVar4 + 1;
      piVar5 = piVar5 + 0x15;
    } while (iVar4 < unaff_ESI[0xf]);
  }
  if (0 < unaff_ESI[0xf]) {
    puVar6 = (undefined4 *)(unaff_ESI[0x11] + 0x24);
    iVar4 = 0;
    do {
      iVar3 = unaff_ESI[7];
      iVar1 = unaff_ESI[0x3c];
      puVar6[-8] = iVar4;
      *puVar6 = 8;
      iVar1 = CDXTexture__CeilDiv(puVar6[-7] * iVar3,iVar1 << 3);
      iVar3 = unaff_ESI[0x3d];
      puVar6[-2] = iVar1;
      iVar2 = CDXTexture__CeilDiv(puVar6[-6] * unaff_ESI[8],iVar3 << 3);
      iVar3 = unaff_ESI[7];
      iVar1 = unaff_ESI[0x3c];
      puVar6[-1] = iVar2;
      iVar1 = CDXTexture__CeilDiv(puVar6[-7] * iVar3,iVar1);
      iVar3 = unaff_ESI[8];
      puVar6[1] = iVar1;
      iVar3 = CDXTexture__CeilDiv(puVar6[-6] * iVar3,unaff_ESI[0x3d]);
      puVar6[2] = iVar3;
      iVar3 = unaff_ESI[0xf];
      puVar6[3] = 1;
      iVar4 = iVar4 + 1;
      puVar6 = puVar6 + 0x15;
    } while (iVar4 < iVar3);
  }
  iVar4 = CDXTexture__CeilDiv(unaff_ESI[8],unaff_ESI[0x3d] << 3);
  unaff_ESI[0x3e] = iVar4;
  return;
}

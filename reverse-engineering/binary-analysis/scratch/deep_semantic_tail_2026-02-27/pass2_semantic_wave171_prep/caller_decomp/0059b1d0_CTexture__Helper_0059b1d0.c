/* address: 0x0059b1d0 */
/* name: CTexture__Helper_0059b1d0 */
/* signature: void CTexture__Helper_0059b1d0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__Helper_0059b1d0(void)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int extraout_ECX;
  int iVar5;
  int *unaff_ESI;

  iVar1 = unaff_ESI[0x6a];
  CTexture__Helper_0059af40(unaff_ESI);
  CTexture__Helper_0059b150();
  *(undefined4 *)(iVar1 + 0xc) = 0;
  iVar4 = CTexture__Helper_0059aec0(extraout_ECX,(int)unaff_ESI);
  *(int *)(iVar1 + 0x10) = iVar4;
  iVar4 = unaff_ESI[0x15];
  *(undefined4 *)(iVar1 + 0x14) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  if ((iVar4 == 0) || (unaff_ESI[0x10] == 0)) {
    unaff_ESI[0x19] = 0;
    unaff_ESI[0x1a] = 0;
    unaff_ESI[0x1b] = 0;
  }
  if (iVar4 == 0) goto LAB_0059b264;
  if (unaff_ESI[0x11] != 0) {
    puVar2 = (undefined4 *)*unaff_ESI;
    puVar2[5] = 0x2f;
    (*(code *)*puVar2)();
  }
  if (unaff_ESI[0x1e] == 3) {
    if (unaff_ESI[0x22] == 0) {
      if (unaff_ESI[0x17] == 0) goto LAB_0059b236;
      unaff_ESI[0x1b] = 1;
    }
    else {
      unaff_ESI[0x1a] = 1;
    }
  }
  else {
    unaff_ESI[0x1a] = 0;
    unaff_ESI[0x1b] = 0;
    unaff_ESI[0x22] = 0;
LAB_0059b236:
    unaff_ESI[0x19] = 1;
  }
  if (unaff_ESI[0x19] != 0) {
    puVar2 = (undefined4 *)*unaff_ESI;
    puVar2[5] = 0x30;
    (*(code *)*puVar2)();
  }
  if ((unaff_ESI[0x1b] != 0) || (unaff_ESI[0x1a] != 0)) {
    puVar2 = (undefined4 *)*unaff_ESI;
    puVar2[5] = 0x30;
    (*(code *)*puVar2)();
  }
LAB_0059b264:
  if (unaff_ESI[0x11] == 0) {
    if (*(int *)(iVar1 + 0x10) == 0) {
      CTexture__Helper_005b0ee0(unaff_ESI);
      CTexture__Helper_005af670(unaff_ESI);
    }
    else {
      CDXTexture__InitColorTransformContext((int)unaff_ESI);
    }
    CTexture__Helper_005ae780(unaff_ESI);
  }
  CTexture__Helper_005ae600((int)unaff_ESI);
  if (unaff_ESI[0x39] == 0) {
    if (unaff_ESI[0x38] == 0) {
      CDXTexture__Helper_005ad550((int)unaff_ESI);
    }
    else {
      CTexture__Helper_005ae190((int)unaff_ESI);
    }
  }
  else {
    puVar2 = (undefined4 *)*unaff_ESI;
    puVar2[5] = 1;
    (*(code *)*puVar2)();
  }
  CTexture__Helper_005ac980((int)unaff_ESI);
  if (unaff_ESI[0x11] == 0) {
    CTexture__Helper_005ab9c0(unaff_ESI);
  }
  (**(code **)(unaff_ESI[1] + 0x18))();
  (**(code **)(unaff_ESI[0x6e] + 8))();
  iVar4 = unaff_ESI[2];
  if (((iVar4 != 0) && (unaff_ESI[0x10] == 0)) && (*(int *)(unaff_ESI[0x6e] + 0x10) != 0)) {
    iVar5 = unaff_ESI[9];
    if (unaff_ESI[0x38] != 0) {
      iVar5 = iVar5 * 3 + 2;
    }
    iVar3 = unaff_ESI[0x51];
    *(undefined4 *)(iVar4 + 4) = 0;
    *(int *)(iVar4 + 8) = iVar3 * iVar5;
    iVar5 = unaff_ESI[0x1b];
    *(undefined4 *)(iVar4 + 0xc) = 0;
    *(uint *)(iVar4 + 0x10) = (iVar5 != 0) + 2;
    *(int *)(iVar1 + 0xc) = *(int *)(iVar1 + 0xc) + 1;
  }
  return;
}

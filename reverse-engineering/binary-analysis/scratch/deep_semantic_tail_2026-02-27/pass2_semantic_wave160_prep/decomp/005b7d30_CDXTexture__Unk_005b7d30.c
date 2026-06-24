/* address: 0x005b7d30 */
/* name: CDXTexture__Unk_005b7d30 */
/* signature: uint CDXTexture__Unk_005b7d30(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

uint CDXTexture__Unk_005b7d30(void)

{
  uint uVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int *unaff_ESI;
  uint uStack_8;
  int *piStack_4;

  iVar5 = unaff_ESI[0x3f];
  if (iVar5 == 1) {
    iVar5 = unaff_ESI[0x40];
    uVar1 = *(uint *)(iVar5 + 0xc);
    unaff_ESI[0x44] = *(int *)(iVar5 + 0x1c);
    uVar7 = *(uint *)(iVar5 + 0x20);
    unaff_ESI[0x45] = uVar7;
    uVar4 = uVar7 / uVar1;
    *(undefined4 *)(iVar5 + 0x34) = 1;
    *(undefined4 *)(iVar5 + 0x38) = 1;
    *(undefined4 *)(iVar5 + 0x3c) = 1;
    *(undefined4 *)(iVar5 + 0x40) = 8;
    *(undefined4 *)(iVar5 + 0x44) = 1;
    uVar6 = uVar7 % uVar1;
    if (uVar7 % uVar1 == 0) {
      uVar6 = uVar1;
    }
    *(uint *)(iVar5 + 0x48) = uVar6;
    unaff_ESI[0x46] = 1;
    unaff_ESI[0x47] = 0;
  }
  else {
    if ((iVar5 < 1) || (4 < iVar5)) {
      puVar2 = (undefined4 *)*unaff_ESI;
      puVar2[5] = 0x1a;
      puVar2[6] = iVar5;
      puVar2[7] = 4;
      (*(code *)*puVar2)();
    }
    iVar5 = CDXTexture__Helper_0059c670(unaff_ESI[7],unaff_ESI[0x3c] << 3);
    unaff_ESI[0x44] = iVar5;
    uVar4 = CDXTexture__Helper_0059c670(unaff_ESI[8],unaff_ESI[0x3d] << 3);
    unaff_ESI[0x45] = uVar4;
    unaff_ESI[0x46] = 0;
    uStack_8 = 0;
    if (0 < unaff_ESI[0x3f]) {
      piStack_4 = unaff_ESI + 0x40;
      do {
        iVar5 = *piStack_4;
        uVar4 = *(uint *)(iVar5 + 8);
        uVar1 = *(uint *)(iVar5 + 0xc);
        *(uint *)(iVar5 + 0x40) = uVar4 * 8;
        uVar7 = *(uint *)(iVar5 + 0x1c) % uVar4;
        iVar8 = uVar1 * uVar4;
        *(uint *)(iVar5 + 0x34) = uVar4;
        *(uint *)(iVar5 + 0x38) = uVar1;
        *(int *)(iVar5 + 0x3c) = iVar8;
        if (uVar7 == 0) {
          uVar7 = uVar4;
        }
        *(uint *)(iVar5 + 0x44) = uVar7;
        uVar4 = *(uint *)(iVar5 + 0x20) % uVar1;
        if (uVar4 == 0) {
          uVar4 = uVar1;
        }
        iVar3 = unaff_ESI[0x46];
        *(uint *)(iVar5 + 0x48) = uVar4;
        if (10 < iVar3 + iVar8) {
          puVar2 = (undefined4 *)*unaff_ESI;
          puVar2[5] = 0xd;
          (*(code *)*puVar2)();
        }
        if (0 < iVar8) {
          do {
            unaff_ESI[unaff_ESI[0x46] + 0x47] = uStack_8;
            iVar8 = iVar8 + -1;
            unaff_ESI[0x46] = unaff_ESI[0x46] + 1;
          } while (iVar8 != 0);
        }
        uVar4 = uStack_8 + 1;
        piStack_4 = piStack_4 + 1;
        uStack_8 = uVar4;
      } while ((int)uVar4 < unaff_ESI[0x3f]);
    }
  }
  if (0 < unaff_ESI[0x33]) {
    uVar4 = unaff_ESI[0x44] * unaff_ESI[0x33];
    if (0xfffe < (int)uVar4) {
      uVar4 = 0xffff;
    }
    unaff_ESI[0x32] = uVar4;
  }
  return uVar4;
}

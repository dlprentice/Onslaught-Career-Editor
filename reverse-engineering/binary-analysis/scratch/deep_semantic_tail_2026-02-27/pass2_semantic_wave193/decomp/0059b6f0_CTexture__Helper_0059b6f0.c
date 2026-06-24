/* address: 0x0059b6f0 */
/* name: CTexture__Helper_0059b6f0 */
/* signature: uint CTexture__Helper_0059b6f0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

uint CTexture__Helper_0059b6f0(void)

{
  undefined4 uVar1;
  uint uVar2;
  undefined4 *puVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int *unaff_ESI;
  uint uStack_8;
  int *piStack_4;

  iVar4 = unaff_ESI[0x53];
  if (iVar4 != 1) {
    if ((iVar4 < 1) || (4 < iVar4)) {
      puVar3 = (undefined4 *)*unaff_ESI;
      puVar3[5] = 0x1a;
      puVar3[6] = iVar4;
      puVar3[7] = 4;
      (*(code *)*puVar3)();
    }
    iVar4 = CDXTexture__CeilDiv(unaff_ESI[7],unaff_ESI[0x4e] << 3);
    unaff_ESI[0x58] = iVar4;
    uVar5 = CDXTexture__CeilDiv(unaff_ESI[8],unaff_ESI[0x4f] << 3);
    unaff_ESI[0x59] = uVar5;
    unaff_ESI[0x5a] = 0;
    uStack_8 = 0;
    if (0 < unaff_ESI[0x53]) {
      piStack_4 = unaff_ESI + 0x54;
      do {
        iVar4 = *piStack_4;
        uVar5 = *(uint *)(iVar4 + 8);
        uVar2 = *(uint *)(iVar4 + 0xc);
        *(uint *)(iVar4 + 0x40) = *(int *)(iVar4 + 0x24) * uVar5;
        uVar6 = *(uint *)(iVar4 + 0x1c) % uVar5;
        iVar7 = uVar2 * uVar5;
        *(uint *)(iVar4 + 0x34) = uVar5;
        *(uint *)(iVar4 + 0x38) = uVar2;
        *(int *)(iVar4 + 0x3c) = iVar7;
        if (uVar6 == 0) {
          uVar6 = uVar5;
        }
        *(uint *)(iVar4 + 0x44) = uVar6;
        uVar5 = *(uint *)(iVar4 + 0x20) % uVar2;
        if (uVar5 == 0) {
          uVar5 = uVar2;
        }
        *(uint *)(iVar4 + 0x48) = uVar5;
        if (10 < unaff_ESI[0x5a] + iVar7) {
          puVar3 = (undefined4 *)*unaff_ESI;
          puVar3[5] = 0xd;
          (*(code *)*puVar3)();
        }
        if (0 < iVar7) {
          do {
            unaff_ESI[unaff_ESI[0x5a] + 0x5b] = uStack_8;
            iVar7 = iVar7 + -1;
            unaff_ESI[0x5a] = unaff_ESI[0x5a] + 1;
          } while (iVar7 != 0);
        }
        uVar5 = uStack_8 + 1;
        piStack_4 = piStack_4 + 1;
        uStack_8 = uVar5;
      } while ((int)uVar5 < unaff_ESI[0x53]);
    }
    return uVar5;
  }
  iVar4 = unaff_ESI[0x54];
  uVar1 = *(undefined4 *)(iVar4 + 0x24);
  uVar5 = *(uint *)(iVar4 + 0xc);
  unaff_ESI[0x58] = *(int *)(iVar4 + 0x1c);
  uVar2 = *(uint *)(iVar4 + 0x20);
  *(undefined4 *)(iVar4 + 0x40) = uVar1;
  unaff_ESI[0x59] = uVar2;
  *(undefined4 *)(iVar4 + 0x34) = 1;
  *(undefined4 *)(iVar4 + 0x38) = 1;
  *(undefined4 *)(iVar4 + 0x3c) = 1;
  *(undefined4 *)(iVar4 + 0x44) = 1;
  uVar6 = uVar2 % uVar5;
  if (uVar2 % uVar5 == 0) {
    uVar6 = uVar5;
  }
  unaff_ESI[0x5a] = 1;
  *(uint *)(iVar4 + 0x48) = uVar6;
  unaff_ESI[0x5b] = 0;
  return uVar2 / uVar5;
}

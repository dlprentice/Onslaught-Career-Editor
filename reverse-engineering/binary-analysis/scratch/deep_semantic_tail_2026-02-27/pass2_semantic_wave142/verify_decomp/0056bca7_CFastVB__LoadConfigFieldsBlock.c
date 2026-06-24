/* address: 0x0056bca7 */
/* name: CFastVB__LoadConfigFieldsBlock */
/* signature: uint __cdecl CFastVB__LoadConfigFieldsBlock(int param_1) */


uint __cdecl CFastVB__LoadConfigFieldsBlock(int param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;

  uVar15 = (uint)DAT_009d0b08;
  if (param_1 == 0) {
    uVar15 = 0xffffffff;
  }
  else {
    uVar1 = CTexture__Helper_0056ddc2(1,uVar15,0x15,(void *)(param_1 + 0xc));
    uVar2 = CTexture__Helper_0056ddc2(1,uVar15,0x14,(void *)(param_1 + 0x10));
    uVar3 = CTexture__Helper_0056ddc2(1,uVar15,0x16,(void *)(param_1 + 0x14));
    uVar4 = CTexture__Helper_0056ddc2(1,uVar15,0x17,(void *)(param_1 + 0x18));
    uVar5 = CTexture__Helper_0056ddc2(1,uVar15,0x18,(void *)(param_1 + 0x1c));
    CFastVB__NormalizeDigitStringInPlace(*(void **)(param_1 + 0x1c));
    uVar6 = CTexture__Helper_0056ddc2(1,uVar15,0x50,(void *)(param_1 + 0x20));
    uVar7 = CTexture__Helper_0056ddc2(1,uVar15,0x51,(void *)(param_1 + 0x24));
    uVar8 = CTexture__Helper_0056ddc2(0,uVar15,0x1a,(void *)(param_1 + 0x28));
    uVar9 = CTexture__Helper_0056ddc2(0,uVar15,0x19,(void *)(param_1 + 0x29));
    uVar10 = CTexture__Helper_0056ddc2(0,uVar15,0x54,(void *)(param_1 + 0x2a));
    uVar11 = CTexture__Helper_0056ddc2(0,uVar15,0x55,(void *)(param_1 + 0x2b));
    uVar12 = CTexture__Helper_0056ddc2(0,uVar15,0x56,(void *)(param_1 + 0x2c));
    uVar13 = CTexture__Helper_0056ddc2(0,uVar15,0x57,(void *)(param_1 + 0x2d));
    uVar14 = CTexture__Helper_0056ddc2(0,uVar15,0x52,(void *)(param_1 + 0x2e));
    uVar15 = CTexture__Helper_0056ddc2(0,uVar15,0x53,(void *)(param_1 + 0x2f));
    uVar15 = uVar15 | uVar1 | uVar2 | uVar3 | uVar4 | uVar5 | uVar6 | uVar7 | uVar8 | uVar9 | uVar10
                      | uVar11 | uVar12 | uVar13 | uVar14;
  }
  return uVar15;
}

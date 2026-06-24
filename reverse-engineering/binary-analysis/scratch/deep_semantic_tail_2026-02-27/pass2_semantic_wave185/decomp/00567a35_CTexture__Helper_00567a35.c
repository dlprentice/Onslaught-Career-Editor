/* address: 0x00567a35 */
/* name: CTexture__Helper_00567a35 */
/* signature: void __cdecl CTexture__Helper_00567a35(uint param_1) */


void __cdecl CTexture__Helper_00567a35(uint param_1)

{
  uint *puVar1;
  undefined4 *puVar2;
  int iVar3;

  puVar1 = (uint *)CTexture__Helper_00567ab1();
  iVar3 = 0;
  *puVar1 = param_1;
  puVar1 = &DAT_00655db0;
  do {
    if (param_1 == *puVar1) {
      puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
      *puVar2 = *(undefined4 *)(iVar3 * 8 + 0x655db4);
      return;
    }
    puVar1 = puVar1 + 2;
    iVar3 = iVar3 + 1;
  } while ((int)puVar1 < 0x655f18);
  if ((0x12 < param_1) && (param_1 < 0x25)) {
    puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar2 = 0xd;
    return;
  }
  if ((0xbb < param_1) && (param_1 < 0xcb)) {
    puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar2 = 8;
    return;
  }
  puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar2 = 0x16;
  return;
}

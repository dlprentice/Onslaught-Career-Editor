/* address: 0x00562a89 */
/* name: CDXTexture__Helper_00562a89 */
/* signature: void __cdecl CDXTexture__Helper_00562a89(int param_1) */


void __cdecl CDXTexture__Helper_00562a89(int param_1)

{
  undefined4 *puVar1;

  if (param_1 == 1) {
    puVar1 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar1 = 0x21;
  }
  else if ((1 < param_1) && (param_1 < 4)) {
    puVar1 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar1 = 0x22;
    return;
  }
  return;
}

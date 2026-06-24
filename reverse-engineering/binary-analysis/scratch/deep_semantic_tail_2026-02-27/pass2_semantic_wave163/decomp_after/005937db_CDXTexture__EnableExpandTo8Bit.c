/* address: 0x005937db */
/* name: CDXTexture__EnableExpandTo8Bit */
/* signature: void __stdcall CDXTexture__EnableExpandTo8Bit(int param_1) */


void CDXTexture__EnableExpandTo8Bit(int param_1)

{
  if (*(byte *)(param_1 + 0x117) < 8) {
    *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 4;
    *(undefined1 *)(param_1 + 0x118) = 8;
  }
  return;
}

/* address: 0x00594fdc */
/* name: CDXTexture__SetDecodeOptionByte */
/* signature: void __stdcall CDXTexture__SetDecodeOptionByte(int param_1, int param_2, int param_3) */


void CDXTexture__SetDecodeOptionByte(int param_1,int param_2,int param_3)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    *(byte *)(param_2 + 9) = *(byte *)(param_2 + 9) | 8;
    *(undefined1 *)(param_2 + 0x2c) = (undefined1)param_3;
  }
  return;
}

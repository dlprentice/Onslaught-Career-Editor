/* address: 0x00594fdc */
/* name: CDXTexture__Unk_00594fdc */
/* signature: void __stdcall CDXTexture__Unk_00594fdc(int param_1, int param_2, int param_3) */


void CDXTexture__Unk_00594fdc(int param_1,int param_2,int param_3)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    *(byte *)(param_2 + 9) = *(byte *)(param_2 + 9) | 8;
    *(undefined1 *)(param_2 + 0x2c) = (undefined1)param_3;
  }
  return;
}

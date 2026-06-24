/* address: 0x0059cc68 */
/* name: CDXTexture__FreeDecodeState */
/* signature: void __stdcall CDXTexture__FreeDecodeState(int param_1) */


void CDXTexture__FreeDecodeState(int param_1)

{
  if (param_1 != 0) {
    CRT__FreeBase(param_1);
  }
  return;
}

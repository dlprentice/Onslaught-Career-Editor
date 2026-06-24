/* address: 0x0059517e */
/* name: CDXTexture__FreeDecodeBufferIfPresent */
/* signature: void __stdcall CDXTexture__FreeDecodeBufferIfPresent(int param_1, int param_2) */


void CDXTexture__FreeDecodeBufferIfPresent(int param_1,int param_2)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    CRT__FreeBase(param_2);
  }
  return;
}

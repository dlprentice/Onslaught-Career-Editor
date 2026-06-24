/* address: 0x005937bc */
/* name: CDXTexture__EnableByteSwapTransform */
/* signature: void __stdcall CDXTexture__EnableByteSwapTransform(int param_1) */


void CDXTexture__EnableByteSwapTransform(int param_1)

{
  *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 1;
  return;
}

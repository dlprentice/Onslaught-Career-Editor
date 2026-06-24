/* address: 0x005935a3 */
/* name: CDXTexture__TestDecodeOptionFlagMask */
/* signature: uint __stdcall CDXTexture__TestDecodeOptionFlagMask(int param_1, int param_2, uint param_3) */


uint CDXTexture__TestDecodeOptionFlagMask(int param_1,int param_2,uint param_3)

{
  uint uVar1;

  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    uVar1 = *(uint *)(param_2 + 8) & param_3;
  }
  return uVar1;
}

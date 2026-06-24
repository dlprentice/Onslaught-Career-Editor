/* address: 0x00594ff9 */
/* name: CDXTexture__SetDecodeOptionByteWithDefaultFloat */
/* signature: void __stdcall CDXTexture__SetDecodeOptionByteWithDefaultFloat(int param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CDXTexture__SetDecodeOptionByteWithDefaultFloat(int param_1,int param_2,int param_3)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    CDXTexture__SetDecodeOptionByte(param_1,param_2,param_3);
    CDXTexture__SetDecodeOptionFloat(param_1,param_2,_DAT_005eeb30);
  }
  return;
}

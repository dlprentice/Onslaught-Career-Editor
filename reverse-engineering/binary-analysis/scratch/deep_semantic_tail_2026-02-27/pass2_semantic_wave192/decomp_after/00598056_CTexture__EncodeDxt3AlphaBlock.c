/* address: 0x00598056 */
/* name: CTexture__EncodeDxt3AlphaBlock */
/* signature: void __stdcall CTexture__EncodeDxt3AlphaBlock(void * param_1) */


void CTexture__EncodeDxt3AlphaBlock(void *param_1)

{
  int iVar1;
  undefined1 local_104 [256];

  iVar1 = CTexture__PremultiplyAlphaBlock16(local_104);
  if (-1 < iVar1) {
    CFastVB__PackScalarBlock_4BitEndpoints(param_1,(int)local_104);
  }
  return;
}

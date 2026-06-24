/* address: 0x0059808a */
/* name: CTexture__EncodeDxt5AlphaBlock */
/* signature: int __stdcall CTexture__EncodeDxt5AlphaBlock(void * param_1) */


int CTexture__EncodeDxt5AlphaBlock(void *param_1)

{
  int iVar1;
  undefined1 local_104 [256];

  iVar1 = CTexture__PremultiplyAlphaBlock16(local_104);
  if (-1 < iVar1) {
    iVar1 = CFastVB__PackScalarBlock_InterpolatedEndpoints(param_1,(float)local_104);
    if (-1 < iVar1) {
      iVar1 = 0;
    }
  }
  return iVar1;
}

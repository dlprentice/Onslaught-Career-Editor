/* address: 0x00593024 */
/* name: CDXTexture__Helper_00593024 */
/* signature: void __stdcall CDXTexture__Helper_00593024(int param_1, int param_2) */


void CDXTexture__Helper_00593024(int param_1,int param_2)

{
  if ((*(byte *)(param_1 + 0x5c) & 0x40) == 0) {
    CDXTexture__InitPngImageBuffersAndPassGeometry((void *)param_1);
  }
  CDXTexture__ApplyPngPostprocessLayoutFlags(param_1,(void *)param_2);
  return;
}

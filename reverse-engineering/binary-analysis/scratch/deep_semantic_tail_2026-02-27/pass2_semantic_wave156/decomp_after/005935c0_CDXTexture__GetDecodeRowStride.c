/* address: 0x005935c0 */
/* name: CDXTexture__GetDecodeRowStride */
/* signature: int __stdcall CDXTexture__GetDecodeRowStride(int param_1, int param_2) */


int CDXTexture__GetDecodeRowStride(int param_1,int param_2)

{
  int iVar1;

  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = 0;
  }
  else {
    iVar1 = *(int *)(param_2 + 0xc);
  }
  return iVar1;
}

/* address: 0x005ab0ed */
/* name: CDXTexture__EvalNodeOutputSizeUnits */
/* signature: int __stdcall CDXTexture__EvalNodeOutputSizeUnits(int param_1) */


int CDXTexture__EvalNodeOutputSizeUnits(int param_1)

{
  int iVar1;
  int iVar2;

  while( true ) {
    while( true ) {
      if (param_1 == 0) {
        return 0;
      }
      iVar1 = *(int *)(param_1 + 4);
      if (iVar1 == 1) {
        iVar1 = CDXTexture__EvalNodeOutputSizeUnits(*(int *)(param_1 + 0xc));
        iVar2 = CDXTexture__EvalNodeOutputSizeUnits(*(int *)(param_1 + 8));
        return iVar2 + iVar1;
      }
      if (iVar1 != 5) break;
      param_1 = *(int *)(param_1 + 0x18);
    }
    if (iVar1 == 7) {
      iVar1 = CDXTexture__EvalNodeOutputSizeUnits(*(int *)(param_1 + 0x10));
      return iVar1 * *(int *)(param_1 + 0x14);
    }
    if (iVar1 == 8) break;
    if (iVar1 != 10) {
      return 0;
    }
    param_1 = *(int *)(param_1 + 0x20);
  }
  return *(int *)(param_1 + 0x1c) * *(int *)(param_1 + 0x18);
}

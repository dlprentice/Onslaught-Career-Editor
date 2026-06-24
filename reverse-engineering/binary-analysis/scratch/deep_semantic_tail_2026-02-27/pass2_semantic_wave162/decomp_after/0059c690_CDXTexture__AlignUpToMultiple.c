/* address: 0x0059c690 */
/* name: CDXTexture__AlignUpToMultiple */
/* signature: int __stdcall CDXTexture__AlignUpToMultiple(int param_1, int param_2) */


int CDXTexture__AlignUpToMultiple(int param_1,int param_2)

{
  int iVar1;

  iVar1 = param_1 + -1 + param_2;
  return iVar1 - iVar1 % param_2;
}

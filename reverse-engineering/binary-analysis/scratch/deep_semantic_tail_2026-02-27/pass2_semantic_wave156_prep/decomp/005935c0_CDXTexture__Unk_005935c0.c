/* address: 0x005935c0 */
/* name: CDXTexture__Unk_005935c0 */
/* signature: int __stdcall CDXTexture__Unk_005935c0(int param_1, int param_2) */


int CDXTexture__Unk_005935c0(int param_1,int param_2)

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

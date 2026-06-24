/* address: 0x00504cf0 */
/* name: CVBufTexture__ShouldSkipUpdateByStateFlags */
/* signature: int __fastcall CVBufTexture__ShouldSkipUpdateByStateFlags(int param_1) */


int __fastcall CVBufTexture__ShouldSkipUpdateByStateFlags(int param_1)

{
  int iVar1;

  iVar1 = CVBufTexture__Helper_004fd760(param_1);
  if ((iVar1 == 0) &&
     (((*(int *)(param_1 + 0x168) != 0 || (*(int *)(param_1 + 0x214) == 0)) &&
      ((*(byte *)(param_1 + 0x2c) & 4) == 0)))) {
    return 0;
  }
  return 1;
}

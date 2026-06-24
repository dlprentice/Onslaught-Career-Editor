/* address: 0x005937f6 */
/* name: CDXTexture__Unk_005937f6 */
/* signature: int __stdcall CDXTexture__Unk_005937f6(int param_1) */


int CDXTexture__Unk_005937f6(int param_1)

{
  int iVar1;

  if (*(char *)(param_1 + 0x113) == '\0') {
    iVar1 = 1;
  }
  else {
    *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 2;
    iVar1 = 7;
  }
  return iVar1;
}

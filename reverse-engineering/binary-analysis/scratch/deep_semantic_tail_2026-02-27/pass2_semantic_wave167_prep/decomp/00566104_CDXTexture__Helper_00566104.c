/* address: 0x00566104 */
/* name: CDXTexture__Helper_00566104 */
/* signature: int __cdecl CDXTexture__Helper_00566104(int param_1) */


int __cdecl CDXTexture__Helper_00566104(int param_1)

{
  int iVar1;

  if (DAT_009d09b8 != (code *)0x0) {
    iVar1 = (*DAT_009d09b8)(param_1);
    if (iVar1 != 0) {
      return 1;
    }
  }
  return 0;
}

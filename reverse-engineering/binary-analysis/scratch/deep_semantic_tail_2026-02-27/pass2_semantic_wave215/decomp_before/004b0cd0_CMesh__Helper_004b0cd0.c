/* address: 0x004b0cd0 */
/* name: CMesh__Helper_004b0cd0 */
/* signature: int __fastcall CMesh__Helper_004b0cd0(int param_1) */


int __fastcall CMesh__Helper_004b0cd0(int param_1)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 0x8c);
  if ((iVar1 != 1) && (iVar1 != 3)) {
    if (iVar1 == 6) {
      return *(int *)(param_1 + 0x124);
    }
    param_1 = 0;
  }
  return param_1;
}

/* address: 0x0056ce69 */
/* name: CRT__IsInDst_WrapperLocked */
/* signature: int __cdecl CRT__IsInDst_WrapperLocked(int param_1) */


int __cdecl CRT__IsInDst_WrapperLocked(int param_1)

{
  bool bVar1;
  undefined3 extraout_var;

  CDXTexture__Helper_00561179(0xb);
  bVar1 = CRT__IsInDst((void *)param_1);
  CTexture__Helper_005611da(0xb);
  return CONCAT31(extraout_var,bVar1);
}

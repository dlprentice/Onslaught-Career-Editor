/* address: 0x00563714 */
/* name: CFastVB__Helper_00563714 */
/* signature: uint __cdecl CFastVB__Helper_00563714(uint param_1) */


uint __cdecl CFastVB__Helper_00563714(uint param_1)

{
  uint uVar1;
  void *in_ECX;
  uint unaff_ESI;

  if (DAT_00653a9c < 2) {
    uVar1 = (byte)PTR_DAT_00653890[param_1 * 2] & 4;
  }
  else {
    uVar1 = CRT__GetCharTypeMask_Compat(in_ECX,param_1,4,unaff_ESI);
  }
  if (uVar1 == 0) {
    param_1 = (param_1 & 0xffffffdf) - 7;
  }
  return param_1;
}

/* address: 0x0055e6e2 */
/* name: CFastVB__Helper_0055e6e2 */
/* signature: uint __cdecl CFastVB__Helper_0055e6e2(uint param_1) */


uint __cdecl CFastVB__Helper_0055e6e2(uint param_1)

{
  uint uVar1;
  int iVar2;
  void *in_ECX;
  uint unaff_EBX;

  if (DAT_009d0998 == 0) {
    if ((0x60 < (int)param_1) && ((int)param_1 < 0x7b)) {
      param_1 = param_1 - 0x20;
    }
  }
  else {
    if ((int)param_1 < 0x100) {
      if (DAT_00653a9c < 2) {
        uVar1 = (byte)PTR_DAT_00653890[param_1 * 2] & 2;
      }
      else {
        uVar1 = CRT__GetCharTypeMask_Compat(in_ECX,param_1,2,unaff_EBX);
      }
      if (uVar1 == 0) {
        return param_1;
      }
    }
    iVar2 = CRT__LCMapStringA_Compat();
    if (iVar2 != 0) {
      if (iVar2 == 1) {
        param_1 = (uint)in_ECX & 0xff;
      }
      else {
        param_1 = (uint)in_ECX & 0xffff;
      }
    }
  }
  return param_1;
}

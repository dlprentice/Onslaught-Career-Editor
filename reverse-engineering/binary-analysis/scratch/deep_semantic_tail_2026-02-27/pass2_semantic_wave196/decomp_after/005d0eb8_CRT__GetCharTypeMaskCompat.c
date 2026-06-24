/* address: 0x005d0eb8 */
/* name: CRT__GetCharTypeMaskCompat */
/* signature: uint __cdecl CRT__GetCharTypeMaskCompat(int param_1, int param_2) */


uint __cdecl CRT__GetCharTypeMaskCompat(int param_1,int param_2)

{
  int iVar1;
  uint in_ECX;

  if ((ushort)param_1 == 0xffff) {
    return 0;
  }
  if ((ushort)param_1 < 0x100) {
    in_ECX = (uint)*(ushort *)(PTR_DAT_00653894 + (param_1 & 0xffffU) * 2);
  }
  else {
    iVar1 = CRT__GetStringTypeWideOrAnsiCompat_0056defa();
    if (iVar1 == 0) {
      return 0;
    }
  }
  return in_ECX & 0xffff & param_2 & 0xffffU;
}

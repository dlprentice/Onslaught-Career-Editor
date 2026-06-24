/* address: 0x0056813f */
/* name: CTexture__Helper_0056813f */
/* signature: int __cdecl CTexture__Helper_0056813f(int param_1) */


int __cdecl CTexture__Helper_0056813f(int param_1)

{
  int iVar1;
  bool bVar2;

  if (param_1 == -2) {
    DAT_009d09c0 = 1;
                    /* WARNING: Could not recover jumptable at 0x00568159. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    iVar1 = GetOEMCP();
    return iVar1;
  }
  if (param_1 == -3) {
    DAT_009d09c0 = 1;
                    /* WARNING: Could not recover jumptable at 0x0056816e. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    iVar1 = GetACP();
    return iVar1;
  }
  bVar2 = param_1 == -4;
  if (bVar2) {
    param_1 = DAT_009d09a8;
  }
  DAT_009d09c0 = (uint)bVar2;
  return param_1;
}

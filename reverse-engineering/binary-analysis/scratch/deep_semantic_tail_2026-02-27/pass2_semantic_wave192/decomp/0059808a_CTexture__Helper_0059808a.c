/* address: 0x0059808a */
/* name: CTexture__Helper_0059808a */
/* signature: int __stdcall CTexture__Helper_0059808a(void * param_1) */


int CTexture__Helper_0059808a(void *param_1)

{
  int iVar1;
  undefined1 local_104 [256];

  iVar1 = CTexture__Helper_00596450(local_104);
  if (-1 < iVar1) {
    iVar1 = CFastVB__PackScalarBlock_InterpolatedEndpoints(param_1,(float)local_104);
    if (-1 < iVar1) {
      iVar1 = 0;
    }
  }
  return iVar1;
}

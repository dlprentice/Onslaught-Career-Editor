/* address: 0x00598056 */
/* name: CTexture__Helper_00598056 */
/* signature: void __stdcall CTexture__Helper_00598056(void * param_1) */


void CTexture__Helper_00598056(void *param_1)

{
  int iVar1;
  undefined1 local_104 [256];

  iVar1 = CTexture__Helper_00596450(local_104);
  if (-1 < iVar1) {
    CFastVB__PackScalarBlock_4BitEndpoints(param_1,(int)local_104);
  }
  return;
}

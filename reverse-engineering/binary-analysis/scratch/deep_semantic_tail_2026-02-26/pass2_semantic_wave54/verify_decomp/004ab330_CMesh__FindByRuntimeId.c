/* address: 0x004ab330 */
/* name: CMesh__FindByRuntimeId */
/* signature: int __cdecl CMesh__FindByRuntimeId(int param_1) */


int __cdecl CMesh__FindByRuntimeId(int param_1)

{
  int iVar1;

  iVar1 = DAT_00704ad8;
  while( true ) {
    if (iVar1 == 0) {
      return 0;
    }
    if (*(int *)(iVar1 + 0x154) == param_1) break;
    iVar1 = *(int *)(iVar1 + 0x158);
  }
  return iVar1;
}

/* address: 0x0056f540 */
/* name: CFastVB__FindEdgeRecord */
/* signature: int __cdecl CFastVB__FindEdgeRecord(int param_1, int param_2, int param_3) */


int __cdecl CFastVB__FindEdgeRecord(int param_1,int param_2,int param_3)

{
  int iVar1;

  iVar1 = *(int *)(*(int *)(param_1 + 4) + param_2 * 4);
  while( true ) {
    while( true ) {
      if (iVar1 == 0) {
        return 0;
      }
      if (*(int *)(iVar1 + 0xc) == param_2) break;
      if (*(int *)(iVar1 + 0xc) == param_3) {
        return iVar1;
      }
      iVar1 = *(int *)(iVar1 + 0x18);
    }
    if (*(int *)(iVar1 + 0x10) == param_3) break;
    iVar1 = *(int *)(iVar1 + 0x14);
  }
  return iVar1;
}

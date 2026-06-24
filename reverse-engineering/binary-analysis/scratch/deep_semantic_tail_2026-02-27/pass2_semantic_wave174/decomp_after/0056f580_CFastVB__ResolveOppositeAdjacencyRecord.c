/* address: 0x0056f580 */
/* name: CFastVB__ResolveOppositeAdjacencyRecord */
/* signature: int __cdecl CFastVB__ResolveOppositeAdjacencyRecord(int param_1, int param_2, int param_3, int param_4) */


int __cdecl CFastVB__ResolveOppositeAdjacencyRecord(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;

  iVar1 = CFastVB__FindEdgeRecord(param_1,param_2,param_3);
  if ((iVar1 == 0) && (param_2 == param_3)) {
    return 0;
  }
  if (*(int *)(iVar1 + 4) == param_4) {
    return *(int *)(iVar1 + 8);
  }
  return *(int *)(iVar1 + 4);
}

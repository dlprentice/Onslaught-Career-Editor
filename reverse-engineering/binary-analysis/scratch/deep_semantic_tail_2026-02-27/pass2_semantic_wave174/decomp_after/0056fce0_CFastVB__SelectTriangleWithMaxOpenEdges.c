/* address: 0x0056fce0 */
/* name: CFastVB__SelectTriangleWithMaxOpenEdges */
/* signature: uint __stdcall CFastVB__SelectTriangleWithMaxOpenEdges(int param_1, int param_2) */


uint CFastVB__SelectTriangleWithMaxOpenEdges(int param_1,int param_2)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint local_14;
  uint local_10;
  uint local_c;

  local_10 = 0xffffffff;
  local_c = 0xffffffff;
  iVar1 = *(int *)(param_1 + 4);
  for (local_14 = 0; (iVar1 != 0 && (local_14 < (uint)(*(int *)(param_1 + 8) - iVar1 >> 2)));
      local_14 = local_14 + 1) {
    piVar2 = *(int **)(iVar1 + local_14 * 4);
    iVar5 = piVar2[1];
    iVar3 = *piVar2;
    iVar4 = CFastVB__ResolveOppositeAdjacencyRecord(param_2,iVar3,iVar5,(int)piVar2);
    uVar6 = (uint)(iVar4 == 0);
    iVar4 = piVar2[2];
    iVar5 = CFastVB__ResolveOppositeAdjacencyRecord(param_2,iVar5,iVar4,(int)piVar2);
    if (iVar5 == 0) {
      uVar6 = uVar6 + 1;
    }
    iVar5 = CFastVB__ResolveOppositeAdjacencyRecord(param_2,iVar4,iVar3,(int)piVar2);
    if (iVar5 == 0) {
      uVar6 = uVar6 + 1;
    }
    if ((int)local_10 < (int)uVar6) {
      local_c = local_14;
      local_10 = uVar6;
    }
  }
  if (local_10 == 0) {
    return 0xffffffff;
  }
  return local_c;
}

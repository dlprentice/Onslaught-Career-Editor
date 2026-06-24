/* address: 0x00572500 */
/* name: CFastVB__CountResolvedOppositeEdges */
/* signature: char __stdcall CFastVB__CountResolvedOppositeEdges(void * param_1, int param_2) */


char CFastVB__CountResolvedOppositeEdges(void *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  char cVar4;

  iVar3 = *(int *)((int)param_1 + 4);
  iVar1 = *(int *)param_1;
  iVar2 = CFastVB__ResolveOppositeAdjacencyRecord(param_2,iVar1,iVar3,(int)param_1);
  cVar4 = iVar2 != 0;
  iVar2 = *(int *)((int)param_1 + 8);
  iVar3 = CFastVB__ResolveOppositeAdjacencyRecord(param_2,iVar3,iVar2,(int)param_1);
  if (iVar3 != 0) {
    cVar4 = cVar4 + '\x01';
  }
  iVar3 = CFastVB__ResolveOppositeAdjacencyRecord(param_2,iVar2,iVar1,(int)param_1);
  if (iVar3 != 0) {
    cVar4 = cVar4 + '\x01';
  }
  return cVar4;
}

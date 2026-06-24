/* address: 0x0056ff40 */
/* name: CFastVB__TriangleListContainsVertexTriplet_0056ff40 */
/* signature: int __stdcall CFastVB__TriangleListContainsVertexTriplet_0056ff40(int param_1, void * param_2) */


int CFastVB__TriangleListContainsVertexTriplet_0056ff40(int param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  bool bVar3;
  bool bVar4;
  char cVar5;
  int *in_EAX;
  uint3 uVar6;
  int *piVar7;

  bVar3 = false;
  iVar1 = *(int *)(param_1 + 4);
  cVar5 = '\0';
  bVar4 = false;
  piVar7 = (int *)0x0;
  do {
    if ((iVar1 == 0) || (in_EAX = (int *)(*(int *)(param_1 + 8) - iVar1 >> 2), in_EAX <= piVar7)) {
      return CONCAT31((int3)((uint)in_EAX >> 8),1);
    }
    if (!bVar4) {
      in_EAX = *(int **)(iVar1 + (int)piVar7 * 4);
      iVar2 = *(int *)param_2;
      if (((*in_EAX == iVar2) || (in_EAX[1] == iVar2)) || (in_EAX[2] == iVar2)) {
        bVar4 = true;
      }
    }
    in_EAX = (int *)CONCAT31((int3)((uint)in_EAX >> 8),cVar5);
    if (cVar5 == '\0') {
      in_EAX = *(int **)(iVar1 + (int)piVar7 * 4);
      iVar2 = *(int *)((int)param_2 + 4);
      if (((*in_EAX == iVar2) || (in_EAX[1] == iVar2)) || (in_EAX[2] == iVar2)) {
        cVar5 = '\x01';
      }
    }
    if (!bVar3) {
      in_EAX = *(int **)(iVar1 + (int)piVar7 * 4);
      iVar2 = *(int *)((int)param_2 + 8);
      if (((*in_EAX == iVar2) || (in_EAX[1] == iVar2)) || (in_EAX[2] == iVar2)) {
        bVar3 = true;
      }
    }
    if (bVar4) {
      uVar6 = (uint3)((uint)in_EAX >> 8);
      in_EAX = (int *)CONCAT31(uVar6,cVar5);
      if ((cVar5 != '\0') && (bVar3)) {
        return (uint)uVar6 << 8;
      }
    }
    piVar7 = (int *)((int)piVar7 + 1);
  } while( true );
}

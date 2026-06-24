/* address: 0x00572490 */
/* name: CFastVB__CountTriangleVerticesInSet_00572490 */
/* signature: int __stdcall CFastVB__CountTriangleVerticesInSet_00572490(void * param_1, void * param_2) */


int CFastVB__CountTriangleVerticesInSet_00572490(void *param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;

  iVar1 = *(int *)((int)param_1 + 4);
  iVar2 = 0;
  iVar3 = 0;
  if (0 < iVar1) {
    piVar4 = *(int **)param_1;
    do {
      if (*piVar4 == *(int *)param_2) {
        iVar2 = 1;
        break;
      }
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < iVar1);
  }
  iVar3 = 0;
  if (0 < iVar1) {
    piVar4 = *(int **)param_1;
    do {
      if (*piVar4 == *(int *)((int)param_2 + 4)) {
        iVar2 = iVar2 + 1;
        break;
      }
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < iVar1);
  }
  iVar3 = 0;
  if (0 < iVar1) {
    piVar4 = *(int **)param_1;
    while (*piVar4 != *(int *)((int)param_2 + 8)) {
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
      if (iVar1 <= iVar3) {
        return iVar2;
      }
    }
    iVar2 = iVar2 + 1;
  }
  return iVar2;
}

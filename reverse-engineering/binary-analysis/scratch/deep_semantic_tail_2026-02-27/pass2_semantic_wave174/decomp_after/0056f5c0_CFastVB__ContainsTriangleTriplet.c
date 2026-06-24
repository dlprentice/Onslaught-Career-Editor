/* address: 0x0056f5c0 */
/* name: CFastVB__ContainsTriangleTriplet */
/* signature: uint __stdcall CFastVB__ContainsTriangleTriplet(void * param_1, int param_2) */


uint CFastVB__ContainsTriangleTriplet(void *param_1,int param_2)

{
  int iVar1;
  int *in_EAX;
  int *piVar2;

  piVar2 = (int *)0x0;
  iVar1 = *(int *)(param_2 + 4);
  while( true ) {
    if ((iVar1 == 0) || (in_EAX = (int *)(*(int *)(param_2 + 8) - iVar1 >> 2), in_EAX <= piVar2)) {
      return (uint)in_EAX & 0xffffff00;
    }
    in_EAX = *(int **)(iVar1 + (int)piVar2 * 4);
    if (((*in_EAX == *(int *)param_1) && (in_EAX[1] == *(int *)((int)param_1 + 4))) &&
       (in_EAX = (int *)in_EAX[2], in_EAX == *(int **)((int)param_1 + 8))) break;
    piVar2 = (int *)((int)piVar2 + 1);
  }
  return CONCAT31((int3)((uint)in_EAX >> 8),1);
}

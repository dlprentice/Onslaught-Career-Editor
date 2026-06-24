/* address: 0x0056fe70 */
/* name: CFastVB__AreTriangleVertexSetsEquivalent */
/* signature: int __cdecl CFastVB__AreTriangleVertexSetsEquivalent(void * param_1, void * param_2) */


int __cdecl CFastVB__AreTriangleVertexSetsEquivalent(void *param_1,void *param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = *(int *)param_1;
  iVar2 = *(int *)param_2;
  if (((((iVar2 == iVar1) || (iVar2 == *(int *)((int)param_1 + 4))) ||
       (iVar2 == *(int *)((int)param_1 + 8))) &&
      (((iVar2 = *(int *)((int)param_2 + 4), iVar2 == iVar1 || (iVar2 == *(int *)((int)param_1 + 4))
        ) || (iVar2 == *(int *)((int)param_1 + 8))))) &&
     (((iVar2 = *(int *)((int)param_2 + 8), iVar2 == iVar1 || (iVar2 == *(int *)((int)param_1 + 4)))
      || (iVar2 == *(int *)((int)param_1 + 8))))) {
    iVar2 = -1;
  }
  return iVar2;
}

/* address: 0x00571080 */
/* name: CFastVB__IsDirectedEdgeInTriangle */
/* signature: bool __stdcall CFastVB__IsDirectedEdgeInTriangle(void * param_1, int param_2, int param_3) */


bool CFastVB__IsDirectedEdgeInTriangle(void *param_1,int param_2,int param_3)

{
  if (*(int *)param_1 == param_2) {
    return *(int *)((int)param_1 + 4) == param_3;
  }
  if (*(int *)((int)param_1 + 4) == param_2) {
    return *(int *)((int)param_1 + 8) == param_3;
  }
  return *(int *)param_1 == param_3;
}

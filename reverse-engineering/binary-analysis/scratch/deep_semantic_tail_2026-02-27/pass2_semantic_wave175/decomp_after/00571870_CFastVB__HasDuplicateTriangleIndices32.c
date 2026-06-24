/* address: 0x00571870 */
/* name: CFastVB__HasDuplicateTriangleIndices32 */
/* signature: bool __cdecl CFastVB__HasDuplicateTriangleIndices32(void * param_1) */


bool __cdecl CFastVB__HasDuplicateTriangleIndices32(void *param_1)

{
  if (*(int *)param_1 == *(int *)((int)param_1 + 4)) {
    return true;
  }
  if (*(int *)param_1 == *(int *)((int)param_1 + 8)) {
    return true;
  }
  return *(int *)((int)param_1 + 4) == *(int *)((int)param_1 + 8);
}

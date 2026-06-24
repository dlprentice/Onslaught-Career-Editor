/* address: 0x004aa6b0 */
/* name: CDestructableSegmentsController__FindMeshNameByIdOrUnknown */
/* signature: void * __cdecl CDestructableSegmentsController__FindMeshNameByIdOrUnknown(int segment_id) */


void * __cdecl CDestructableSegmentsController__FindMeshNameByIdOrUnknown(int segment_id)

{
  int iVar1;
  int in_ECX;

  iVar1 = DAT_00704ad8;
  while( true ) {
    if (iVar1 == 0) {
      return s_unknown_mesh_name_0062f8d4;
    }
    if (iVar1 == in_ECX) break;
    iVar1 = *(int *)(iVar1 + 0x158);
  }
  return (void *)(iVar1 + 0x24);
}

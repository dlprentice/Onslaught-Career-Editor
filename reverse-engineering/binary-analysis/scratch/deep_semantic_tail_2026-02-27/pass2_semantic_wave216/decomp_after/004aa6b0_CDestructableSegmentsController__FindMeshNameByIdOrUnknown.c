/* address: 0x004aa6b0 */
/* name: CDestructableSegmentsController__FindMeshNameByIdOrUnknown */
/* signature: char * __fastcall CDestructableSegmentsController__FindMeshNameByIdOrUnknown(int param_1) */


char * __fastcall CDestructableSegmentsController__FindMeshNameByIdOrUnknown(int param_1)

{
  int iVar1;

  iVar1 = DAT_00704ad8;
  while( true ) {
    if (iVar1 == 0) {
      return s_unknown_mesh_name_0062f8d4;
    }
    if (iVar1 == param_1) break;
    iVar1 = *(int *)(iVar1 + 0x158);
  }
  return (char *)(iVar1 + 0x24);
}

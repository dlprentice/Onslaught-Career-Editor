/* address: 0x004aa6b0 */
/* name: CMesh__Unk_004aa6b0 */
/* signature: char * __fastcall CMesh__Unk_004aa6b0(int param_1) */


char * __fastcall CMesh__Unk_004aa6b0(int param_1)

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

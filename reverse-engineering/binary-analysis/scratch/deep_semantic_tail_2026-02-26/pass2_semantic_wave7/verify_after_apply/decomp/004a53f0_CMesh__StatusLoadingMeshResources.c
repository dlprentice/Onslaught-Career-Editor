/* address: 0x004a53f0 */
/* name: CMesh__StatusLoadingMeshResources */
/* signature: void CMesh__StatusLoadingMeshResources(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMesh__StatusLoadingMeshResources(void)

{
  char local_100 [256];

  sprintf(local_100,s_Loading_mesh_resources_0062f9a0);
  CConsole__Status(&DAT_00663498,local_100);
  CConsole__StatusDone(&DAT_00663498,local_100,'\x01');
  return;
}

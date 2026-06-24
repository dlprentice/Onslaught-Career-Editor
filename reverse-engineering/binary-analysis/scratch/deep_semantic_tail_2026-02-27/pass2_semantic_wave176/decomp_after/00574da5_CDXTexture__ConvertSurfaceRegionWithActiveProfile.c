/* address: 0x00574da5 */
/* name: CDXTexture__ConvertSurfaceRegionWithActiveProfile */
/* signature: int CDXTexture__ConvertSurfaceRegionWithActiveProfile(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__ConvertSurfaceRegionWithActiveProfile(void)

{
  int iVar1;
  int iVar2;
  int in_stack_00000004;
  int in_stack_00000010;
  undefined1 local_8 [4];

  CFastVB__Helper_0058c0e4(local_8);
  if ((in_stack_00000004 == 0) || (in_stack_00000010 == 0)) {
    iVar2 = -0x7789f794;
  }
  else {
    iVar1 = CFastVB__Helper_00580ef4();
    if ((iVar1 < 0) || (iVar1 = CDXTexture__ConvertSurfaceWithActiveProfile(), iVar2 = 0, iVar1 < 0)
       ) {
      iVar2 = iVar1;
    }
  }
  CFastVB__ShutdownActiveProfile_Thunk(local_8);
  return iVar2;
}

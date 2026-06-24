/* address: 0x00574662 */
/* name: CDXTexture__ConvertSurfaceWithActiveProfile */
/* signature: int CDXTexture__ConvertSurfaceWithActiveProfile(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__ConvertSurfaceWithActiveProfile(void)

{
  int iVar1;
  undefined4 *puVar2;
  uint unaff_EDI;
  undefined4 *puVar3;
  int in_stack_00000004;
  int in_stack_00000010;
  undefined4 *in_stack_00000024;
  int in_stack_00000028;
  undefined1 local_b4 [68];
  undefined4 local_70;
  undefined1 local_64 [16];
  undefined4 local_54 [6];
  undefined4 local_3c [7];
  undefined4 local_20;
  undefined1 local_14 [12];
  undefined1 local_8 [4];

  CDXTexture__InitMappedFileContext(local_14);
  CFastVB__ResetConversionStatus(local_8);
  if (((in_stack_00000004 == 0) || (in_stack_00000010 == 0)) ||
     (in_stack_00000024 == (undefined4 *)0x0)) {
    iVar1 = -0x7789f794;
  }
  else {
    if (in_stack_00000028 == -1) {
      in_stack_00000028 = 0x80004;
    }
    iVar1 = CDXTexture__CreateTexelCodecProfileFromSurfaceDesc();
    if (-1 < iVar1) {
      puVar2 = in_stack_00000024;
      puVar3 = local_54;
      for (iVar1 = 6; iVar1 != 0; iVar1 = iVar1 + -1) {
        *puVar3 = *puVar2;
        puVar2 = puVar2 + 1;
        puVar3 = puVar3 + 1;
      }
      puVar2 = local_3c;
      for (iVar1 = 6; iVar1 != 0; iVar1 = iVar1 + -1) {
        *puVar2 = *in_stack_00000024;
        in_stack_00000024 = in_stack_00000024 + 1;
        puVar2 = puVar2 + 1;
      }
      local_20 = local_70;
      iVar1 = CFastVB__InitDualTexelConversionPipeline
                        (local_14,local_b4,(int)local_64,in_stack_00000028,unaff_EDI);
      if (-1 < iVar1) {
        iVar1 = 0;
      }
    }
  }
  CFastVB__ShutdownActiveProfile_Thunk(local_8);
  CMeshCollisionVolume__Helper_0057cc5d(local_14);
  return iVar1;
}

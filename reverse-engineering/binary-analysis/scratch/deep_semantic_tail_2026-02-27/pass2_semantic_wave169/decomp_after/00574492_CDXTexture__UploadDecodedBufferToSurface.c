/* address: 0x00574492 */
/* name: CDXTexture__UploadDecodedBufferToSurface */
/* signature: int CDXTexture__UploadDecodedBufferToSurface(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__UploadDecodedBufferToSurface(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  uint unaff_EDI;
  undefined4 *puVar4;
  int in_stack_00000004;
  int in_stack_00000010;
  undefined4 *in_stack_00000020;
  int in_stack_00000024;
  undefined1 local_c4 [68];
  undefined4 local_80;
  undefined1 local_74 [20];
  undefined1 local_60 [12];
  undefined4 local_54;
  undefined4 local_50 [4];
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38 [7];
  undefined4 local_1c;
  undefined1 local_10 [12];

  CDXTexture__InitMappedFileContext(local_10);
  CDXTexture__ResetSurfaceCopyContext(local_74);
  if (in_stack_00000004 == 0) {
    iVar2 = -0x7789f794;
  }
  else if ((in_stack_00000010 == 0) || (in_stack_00000020 == (undefined4 *)0x0)) {
    iVar2 = -0x7789f794;
  }
  else {
    if (in_stack_00000024 == -1) {
      in_stack_00000024 = 0x80004;
    }
    iVar1 = CDXTexture__UploadSurfaceRegionWithFallback();
    if (-1 < iVar1) {
      local_54 = 0;
      local_50[0] = *in_stack_00000020;
      local_50[1] = in_stack_00000020[1];
      local_50[2] = in_stack_00000020[2];
      local_50[3] = in_stack_00000020[3];
      local_40 = 0;
      local_3c = 1;
      puVar3 = local_50;
      puVar4 = local_38;
      for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
        *puVar4 = *puVar3;
        puVar3 = puVar3 + 1;
        puVar4 = puVar4 + 1;
      }
      local_1c = local_80;
      iVar1 = CFastVB__InitDualTexelConversionPipeline
                        (local_10,local_c4,(int)local_60,in_stack_00000024,unaff_EDI);
      iVar2 = 0;
      if (-1 < iVar1) goto LAB_0057455d;
    }
    iVar2 = iVar1;
  }
LAB_0057455d:
  CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(local_74);
  CMeshCollisionVolume__Helper_0057cc5d(local_10);
  return iVar2;
}

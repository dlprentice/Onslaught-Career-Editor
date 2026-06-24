/* address: 0x00574b9d */
/* name: CDXTexture__Helper_00574b9d */
/* signature: int CDXTexture__Helper_00574b9d(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_00574b9d(void)

{
  int *piVar1;
  int iVar2;
  bool bVar3;
  int *in_stack_00000004;
  int *in_stack_00000008;
  int *in_stack_0000000c;
  int *in_stack_00000010;
  int *in_stack_00000014;
  int *in_stack_00000018;
  uint in_stack_0000001c;
  int in_stack_00000020;
  undefined1 local_78 [20];
  undefined1 local_64 [12];
  int local_58;
  int local_4c;
  int local_48;
  undefined1 local_44 [12];
  int local_38;
  int local_2c;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  int local_18;
  int local_14;
  int local_10;
  int local_c;
  int local_8;

  CDXTexture__ResetSurfaceCopyContext(local_78);
  piVar1 = in_stack_00000010;
  if (in_stack_00000004 == (int *)0x0) {
    iVar2 = -0x7789f794;
    goto LAB_00574d93;
  }
  if (in_stack_00000010 == (int *)0x0) {
    iVar2 = -0x7789f794;
    goto LAB_00574d93;
  }
  (**(code **)(*in_stack_00000004 + 0x30))(in_stack_00000004,local_64);
  (**(code **)(*piVar1 + 0x30))(piVar1,local_44);
  if (((in_stack_0000001c & 0xffff) == 5) || (in_stack_00000020 != 0)) {
LAB_00574d08:
    iVar2 = CDXTexture__UploadSurfaceRegionWithFallback();
    if ((iVar2 < 0) || (iVar2 = CDXTexture__UploadDecodedBufferToSurface(), iVar2 < 0))
    goto LAB_00574d93;
    if ((local_38 == 0) && (local_58 != 0)) {
      (**(code **)(*piVar1 + 0xc))(piVar1,&stack0x00000004);
      iVar2 = (**(code **)(*in_stack_00000004 + 0xc))(in_stack_00000004);
      (**(code **)(*in_stack_00000004 + 8))(in_stack_00000004);
      if (iVar2 != 0) {
        iVar2 = -0x7789f798;
        goto LAB_00574d93;
      }
    }
  }
  else {
    if (in_stack_00000008 != in_stack_00000014) {
      if ((in_stack_00000008 != (int *)0x0) && (in_stack_00000014 != (int *)0x0)) {
        iVar2 = 0x100;
        bVar3 = true;
        do {
          if (iVar2 == 0) break;
          iVar2 = iVar2 + -1;
          bVar3 = *in_stack_00000008 == *in_stack_00000014;
          in_stack_00000008 = in_stack_00000008 + 1;
          in_stack_00000014 = in_stack_00000014 + 1;
        } while (bVar3);
        if (bVar3) goto LAB_00574c2d;
      }
      goto LAB_00574d08;
    }
LAB_00574c2d:
    if (in_stack_0000000c == (int *)0x0) {
      local_14 = 0;
      local_10 = 0;
      local_c = local_4c;
      local_8 = local_48;
    }
    else {
      local_14 = *in_stack_0000000c;
      local_10 = in_stack_0000000c[1];
      local_c = in_stack_0000000c[2];
      local_8 = in_stack_0000000c[3];
    }
    if (in_stack_00000018 == (int *)0x0) {
      local_24 = 0;
      local_20 = 0;
      local_1c = local_2c;
      local_18 = local_28;
    }
    else {
      local_24 = *in_stack_00000018;
      local_20 = in_stack_00000018[1];
      local_1c = in_stack_00000018[2];
      local_18 = in_stack_00000018[3];
    }
    if ((local_c - local_14 != local_1c - local_24) || (local_8 - local_10 != local_18 - local_20))
    goto LAB_00574d08;
    (**(code **)(*piVar1 + 0xc))(piVar1,&stack0x00000010);
    CFastVB__Helper_00579bd5(1);
    iVar2 = -0x7fffbffb;
    if (local_58 == 0) {
      if (local_38 == 0) {
        iVar2 = (**(code **)(*in_stack_00000010 + 0x88))
                          (in_stack_00000010,piVar1,&local_24,in_stack_00000004,&local_14,0);
      }
      else if (local_38 == 2) {
        iVar2 = (**(code **)(*in_stack_00000010 + 0x78))
                          (in_stack_00000010,piVar1,&local_24,in_stack_00000004,&local_14);
      }
    }
    CFastVB__Helper_00579bd5(0);
    (**(code **)(*in_stack_00000010 + 8))(in_stack_00000010);
    if (iVar2 < 0) goto LAB_00574d08;
  }
  iVar2 = 0;
LAB_00574d93:
  CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(local_78);
  return iVar2;
}

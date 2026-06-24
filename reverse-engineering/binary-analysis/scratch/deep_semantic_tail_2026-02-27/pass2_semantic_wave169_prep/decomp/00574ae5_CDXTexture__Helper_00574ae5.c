/* address: 0x00574ae5 */
/* name: CDXTexture__Helper_00574ae5 */
/* signature: int CDXTexture__Helper_00574ae5(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Helper_00574ae5(void)

{
  int iVar1;
  int in_stack_00000004;
  int in_stack_00000010;
  int in_stack_00000014;
  int *in_stack_00000018;
  undefined1 local_68 [12];
  int local_5c;
  int local_58;
  int local_50;
  int iStack_4c;
  int iStack_48;
  int iStack_44;
  int local_14;
  int local_10;
  int local_c;
  int local_8;

  CDXTexture__Helper_00579ca5(local_68);
  if (((in_stack_00000004 == 0) || (in_stack_00000010 == 0)) || (in_stack_00000014 == 0)) {
LAB_00574b54:
    iVar1 = -0x7789f794;
  }
  else {
    iVar1 = CDXTexture__DecodeFromMemory_WithFallbackCodecs();
    if (iVar1 < 0) goto LAB_00574b59;
    if (in_stack_00000018 == (int *)0x0) {
      local_14 = local_50;
      local_10 = iStack_4c;
      local_c = iStack_48;
      local_8 = iStack_44;
    }
    else {
      local_14 = *in_stack_00000018;
      local_10 = in_stack_00000018[1];
      local_c = in_stack_00000018[2];
      local_8 = in_stack_00000018[3];
      if ((((local_14 < 0) || (local_5c < local_c)) ||
          ((local_c < local_14 || ((local_10 < 0 || (local_58 < local_8)))))) ||
         (local_8 < local_10)) goto LAB_00574b54;
    }
    iVar1 = CDXTexture__Helper_00574492();
    if (-1 < iVar1) {
      iVar1 = 0;
    }
  }
LAB_00574b59:
  CDXTexture__Helper_00579cbe((int)local_68);
  return iVar1;
}

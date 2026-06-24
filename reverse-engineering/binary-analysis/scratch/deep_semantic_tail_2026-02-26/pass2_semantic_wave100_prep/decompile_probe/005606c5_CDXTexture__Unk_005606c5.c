/* address: 0x005606c5 */
/* name: CDXTexture__Unk_005606c5 */
/* signature: int CDXTexture__Unk_005606c5(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_005606c5(void)

{
  void *pvVar1;
  int extraout_EAX;
  int iVar2;
  void *in_stack_00000004;
  void *in_stack_00000008;
  void *in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  void *in_stack_00000018;
  void *in_stack_0000001c;
  int *in_stack_00000020;
  void *in_stack_00000028;

  if (in_stack_0000001c != (void *)0x0) {
    CDXTexture__Helper_00560885
              ((int)in_stack_00000004,(int)in_stack_00000008,in_stack_00000018,in_stack_0000001c);
  }
  if (in_stack_00000028 == (void *)0x0) {
    in_stack_00000028 = in_stack_00000008;
  }
  CRT__SehRtlUnwindAndRestoreFrame((int)in_stack_00000028,(int)in_stack_00000004);
  CDXTexture__Unk_00560627
            ((int)in_stack_00000008,in_stack_00000010,in_stack_00000014,*in_stack_00000020);
  *(int *)((int)in_stack_00000008 + 8) = in_stack_00000020[1] + 1;
  pvVar1 = (void *)CDXTexture__Helper_00560740
                             (in_stack_00000004,in_stack_00000008,in_stack_0000000c);
  iVar2 = 0;
  if (pvVar1 != (void *)0x0) {
    CRT__SehPopExceptionFrameAndJump(pvVar1);
    iVar2 = extraout_EAX;
  }
  return iVar2;
}

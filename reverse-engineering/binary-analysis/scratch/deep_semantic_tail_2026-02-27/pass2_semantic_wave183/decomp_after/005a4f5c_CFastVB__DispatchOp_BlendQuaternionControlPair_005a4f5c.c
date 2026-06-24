/* address: 0x005a4f5c */
/* name: CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c */
/* signature: int CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c(void)

{
  int extraout_EAX;
  ulonglong uVar1;
  undefined8 uVar2;
  void *in_stack_00000004;
  void *in_stack_00000008;
  void *in_stack_0000000c;
  void *in_stack_00000010;
  void *in_stack_00000014;
  uint in_stack_00000018;
  undefined1 local_20 [16];
  undefined1 local_10 [16];

  CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98
            (local_20,in_stack_00000008,in_stack_00000014,in_stack_00000018);
  CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98
            (local_10,in_stack_0000000c,in_stack_00000010,in_stack_00000018);
  uVar1 = (ulonglong)in_stack_00000018;
  uVar2 = PackedFloatingMUL(uVar1,uVar1);
  uVar2 = PackedFloatingSUB(uVar1,uVar2);
  uVar2 = PackedFloatingMUL(uVar2,_DAT_005ef108);
  CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98
            (in_stack_00000004,local_20,local_10,(uint)uVar2);
  FastExitMediaState();
  return extraout_EAX;
}

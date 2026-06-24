/* address: 0x005a4ecf */
/* name: CFastVB__Helper_005a4ecf */
/* signature: int CFastVB__Helper_005a4ecf(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_005a4ecf(void)

{
  ulonglong uVar1;
  undefined8 uVar2;
  undefined8 in_MM2;
  undefined8 uVar3;
  void *in_stack_00000004;
  void *in_stack_00000008;
  void *in_stack_0000000c;
  void *in_stack_00000010;
  uint in_stack_00000014;
  uint in_stack_00000018;
  undefined1 local_28 [16];
  undefined1 local_18 [20];

  FastExitMediaState();
  uVar1 = PackedFloatingADD((ulonglong)in_stack_00000014,(ulonglong)in_stack_00000018);
  CFastVB__Helper_005a4d98(local_28,in_stack_00000008,in_stack_0000000c,(uint)uVar1);
  CFastVB__Helper_005a4d98(local_18,in_stack_00000008,in_stack_00000010,(uint)uVar1);
  uVar3 = FloatingReciprocalAprox(in_MM2,uVar1 & 0xffffffff);
  uVar2 = PackedFloatingReciprocalIter1(uVar1 & 0xffffffff,uVar3);
  uVar2 = PackedFloatingReciprocalIter2(uVar2,uVar3);
  uVar2 = PackedFloatingMUL(uVar2,(ulonglong)in_stack_00000018);
  CFastVB__Helper_005a4d98(in_stack_00000004,local_28,local_18,(uint)uVar2);
  FastExitMediaState();
  return (int)in_stack_00000004;
}

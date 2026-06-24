/* address: 0x005aa2f2 */
/* name: CFastVB__Unk_005aa2f2 */
/* signature: int CFastVB__Unk_005aa2f2(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Unk_005aa2f2(void)

{
  ulonglong uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined4 uVar6;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 in_MM5;
  undefined8 uVar7;
  undefined8 in_MM6;
  ulonglong *in_stack_00000004;
  ulonglong *in_stack_00000008;
  undefined8 *in_stack_0000000c;
  undefined1 *in_stack_00000010;
  undefined1 *in_stack_00000014;
  undefined1 *in_stack_00000018;
  undefined1 local_44 [64];

  switch(((in_stack_00000018 != (undefined1 *)0x0) << 1 | in_stack_00000014 != (undefined1 *)0x0) <<
         1 | in_stack_00000010 != (undefined1 *)0x0) {
  case '\0':
    CFastVB__Helper_005a62bf(local_44);
    goto switchD_005aa328_default;
  case '\x01':
    in_stack_00000018 = in_stack_00000010;
    goto LAB_005aa36b;
  case '\x02':
    in_stack_00000018 = in_stack_00000014;
    goto LAB_005aa36b;
  case '\x03':
    in_stack_00000018 = in_stack_00000014;
    break;
  case '\x04':
    goto LAB_005aa36b;
  case '\x05':
    break;
  case '\x06':
    in_stack_00000010 = in_stack_00000014;
    break;
  case '\a':
    CFastVB__Helper_005a9d78(local_44,in_stack_00000018,in_stack_00000014);
    in_stack_00000018 = local_44;
    break;
  default:
    goto switchD_005aa328_default;
  }
  CFastVB__Helper_005a9d78(local_44,in_stack_00000018,in_stack_00000010);
  in_stack_00000018 = local_44;
LAB_005aa36b:
  CFastVB__Helper_005a8f5d(local_44,(void *)0x0,in_stack_00000018);
switchD_005aa328_default:
  if (in_stack_0000000c != (undefined8 *)0x0) {
    FastExitMediaState();
    uVar2 = PackedIntToFloatingDwordConv(*in_stack_0000000c,*in_stack_0000000c);
    uVar5 = in_stack_0000000c[2];
    uVar3 = PackedIntToFloatingDwordConv(in_stack_0000000c[1],in_stack_0000000c[1]);
    uVar6 = (undefined4)((ulonglong)uVar3 >> 0x20);
    uVar4 = CONCAT44(uVar6,uVar6);
    uVar7 = FloatingReciprocalAprox(in_MM5,uVar3);
    uVar4 = FloatingReciprocalAprox(uVar4,uVar4);
    uVar2 = PackedFloatingSUB(*in_stack_00000008,uVar2);
    uVar4 = CONCAT44((int)uVar4,(int)uVar7);
    uVar3 = PackedFloatingReciprocalIter1(uVar3,uVar4);
    uVar3 = PackedFloatingReciprocalIter2(uVar3,uVar4);
    uVar3 = PackedFloatingMUL(uVar3,DAT_005ef198);
    uVar2 = PackedFloatingMUL(uVar2,uVar3);
    uVar6 = (undefined4)((ulonglong)uVar5 >> 0x20);
    uVar1 = PackedFloatingSUB(uVar2,_DAT_005ef188);
    uVar2 = PackedFloatingSUB(CONCAT44(uVar6,uVar6),uVar5);
    uVar3 = FloatingReciprocalAprox(in_MM6,uVar2);
    uVar2 = PackedFloatingReciprocalIter1(uVar2,uVar3);
    uVar2 = PackedFloatingReciprocalIter2(uVar2,uVar3);
    uVar5 = PackedFloatingSUB((ulonglong)(uint)in_stack_00000008[1],uVar5);
    uVar5 = PackedFloatingMUL(uVar5,uVar2);
    *in_stack_00000004 = uVar1 ^ DAT_005ef180;
    *(int *)(in_stack_00000004 + 1) = (int)uVar5;
    FastExitMediaState();
    in_stack_00000008 = in_stack_00000004;
  }
  CFastVB__Helper_005a9ced(in_stack_00000004,in_stack_00000008,local_44);
  return (int)in_stack_00000004;
}

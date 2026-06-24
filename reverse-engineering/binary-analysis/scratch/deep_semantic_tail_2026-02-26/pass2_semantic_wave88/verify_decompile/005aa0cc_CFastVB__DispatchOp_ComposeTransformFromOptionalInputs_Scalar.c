/* address: 0x005aa0cc */
/* name: CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar */
/* signature: int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar(void)

{
  undefined8 uVar1;
  undefined8 uVar2;
  ulonglong uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined4 uVar7;
  undefined8 uVar6;
  undefined8 uVar8;
  unkbyte10 in_ST5;
  undefined8 uVar9;
  unkbyte10 in_ST6;
  ulonglong *in_stack_00000004;
  ulonglong *in_stack_00000008;
  undefined8 *in_stack_0000000c;
  void *in_stack_00000010;
  void *in_stack_00000014;
  void *in_stack_00000018;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;

  uVar2 = (undefined8)in_ST5;
  uVar9 = (undefined8)in_ST6;
  switch(((in_stack_00000018 != (void *)0x0) << 1 | in_stack_00000014 != (void *)0x0) << 1 |
         in_stack_00000010 != (void *)0x0) {
  case '\0':
    local_c = 0;
    local_10 = 0;
    local_14 = 0;
    local_18 = 0;
    local_20 = 0;
    local_24 = 0;
    local_28 = 0;
    local_2c = 0;
    local_34 = 0;
    local_38 = 0;
    local_3c = 0;
    local_40 = 0;
    local_8 = 0x3f800000;
    local_1c = 0x3f800000;
    local_30 = 0x3f800000;
    local_44 = 0x3f800000;
    break;
  case '\x01':
    FastExitMediaState();
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,in_stack_00000010);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
    break;
  case '\x02':
    FastExitMediaState();
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,in_stack_00000014);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
    break;
  case '\x03':
    FastExitMediaState();
    CFastVB__Helper_005a9d78(&local_44,in_stack_00000014,in_stack_00000010);
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,&local_44);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
    break;
  case '\x04':
    FastExitMediaState();
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,in_stack_00000018);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
    break;
  case '\x05':
    FastExitMediaState();
    CFastVB__Helper_005a9d78(&local_44,in_stack_00000018,in_stack_00000010);
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,&local_44);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
    break;
  case '\x06':
    FastExitMediaState();
    CFastVB__Helper_005a9d78(&local_44,in_stack_00000018,in_stack_00000014);
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,&local_44);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
    break;
  case '\a':
    FastExitMediaState();
    CFastVB__Helper_005a9d78(&local_44,in_stack_00000018,in_stack_00000014);
    CFastVB__Helper_005a9d78(&local_44,&local_44,in_stack_00000010);
    CFastVB__Helper_005a9637(&local_44,(void *)0x0,&local_44);
    uVar2 = (undefined8)in_ST5;
    uVar9 = (undefined8)in_ST6;
    FastExitMediaState();
  }
  if (in_stack_0000000c != (undefined8 *)0x0) {
    FastExitMediaState();
    uVar4 = PackedIntToFloatingDwordConv(*in_stack_0000000c,*in_stack_0000000c);
    uVar1 = in_stack_0000000c[2];
    uVar5 = PackedIntToFloatingDwordConv(in_stack_0000000c[1],in_stack_0000000c[1]);
    uVar7 = (undefined4)((ulonglong)uVar5 >> 0x20);
    uVar6 = CONCAT44(uVar7,uVar7);
    uVar8 = FloatingReciprocalAprox(uVar2,uVar5);
    uVar6 = FloatingReciprocalAprox(uVar6,uVar6);
    uVar2 = PackedFloatingSUB(*in_stack_00000008,uVar4);
    uVar6 = CONCAT44((int)uVar6,(int)uVar8);
    uVar4 = PackedFloatingReciprocalIter1(uVar5,uVar6);
    uVar4 = PackedFloatingReciprocalIter2(uVar4,uVar6);
    uVar4 = PackedFloatingMUL(uVar4,DAT_005ef198);
    uVar2 = PackedFloatingMUL(uVar2,uVar4);
    uVar7 = (undefined4)((ulonglong)uVar1 >> 0x20);
    uVar3 = PackedFloatingSUB(uVar2,_DAT_005ef188);
    uVar2 = PackedFloatingSUB(CONCAT44(uVar7,uVar7),uVar1);
    uVar9 = FloatingReciprocalAprox(uVar9,uVar2);
    uVar2 = PackedFloatingReciprocalIter1(uVar2,uVar9);
    uVar9 = PackedFloatingReciprocalIter2(uVar2,uVar9);
    uVar2 = PackedFloatingSUB((ulonglong)(uint)in_stack_00000008[1],uVar1);
    uVar2 = PackedFloatingMUL(uVar2,uVar9);
    *in_stack_00000004 = uVar3 ^ DAT_005ef180;
    *(int *)(in_stack_00000004 + 1) = (int)uVar2;
    FastExitMediaState();
    in_stack_00000008 = in_stack_00000004;
  }
  CFastVB__Helper_005a9ced(in_stack_00000004,in_stack_00000008,&local_44);
  return (int)in_stack_00000004;
}

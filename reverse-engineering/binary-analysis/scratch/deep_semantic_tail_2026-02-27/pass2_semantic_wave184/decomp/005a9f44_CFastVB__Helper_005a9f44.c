/* address: 0x005a9f44 */
/* name: CFastVB__Helper_005a9f44 */
/* signature: int CFastVB__Helper_005a9f44(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_005a9f44(void)

{
  undefined4 *puVar1;
  undefined8 uVar2;
  ulonglong uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined4 uVar8;
  undefined8 uVar7;
  ulonglong *in_stack_00000004;
  void *in_stack_00000008;
  undefined8 *in_stack_0000000c;
  undefined4 *in_stack_00000010;
  undefined4 *in_stack_00000014;
  undefined4 *in_stack_00000018;
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

  puVar1 = &local_44;
  switch(((in_stack_00000018 != (undefined4 *)0x0) << 1 | in_stack_00000014 != (undefined4 *)0x0) <<
         1 | in_stack_00000010 != (undefined4 *)0x0) {
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
    puVar1 = in_stack_00000010;
    break;
  case '\x02':
    puVar1 = in_stack_00000014;
    break;
  case '\x03':
    FastExitMediaState();
    CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78
              (&local_44,in_stack_00000014,in_stack_00000010);
    FastExitMediaState();
    break;
  case '\x04':
    puVar1 = in_stack_00000018;
    break;
  case '\x05':
    FastExitMediaState();
    CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78
              (&local_44,in_stack_00000018,in_stack_00000010);
    FastExitMediaState();
    break;
  case '\x06':
    FastExitMediaState();
    CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78
              (&local_44,in_stack_00000018,in_stack_00000014);
    FastExitMediaState();
    break;
  case '\a':
    FastExitMediaState();
    CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78
              (&local_44,in_stack_00000018,in_stack_00000014);
    CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78(&local_44,&local_44,in_stack_00000010);
    FastExitMediaState();
  }
  CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced
            (in_stack_00000004,in_stack_00000008,puVar1);
  if (in_stack_0000000c != (undefined8 *)0x0) {
    FastExitMediaState();
    uVar4 = in_stack_0000000c[2];
    uVar5 = PackedIntToFloatingDwordConv(*in_stack_0000000c,*in_stack_0000000c);
    uVar6 = PackedIntToFloatingDwordConv(in_stack_0000000c[1],in_stack_0000000c[1]);
    uVar2 = PackedFloatingADD(*in_stack_00000004 ^ DAT_005ef180,_DAT_005ef188);
    uVar6 = PackedFloatingMUL(uVar6,DAT_005ef190);
    uVar8 = (undefined4)((ulonglong)uVar4 >> 0x20);
    uVar7 = PackedFloatingSUB(CONCAT44(uVar8,uVar8),uVar4);
    uVar2 = PackedFloatingMUL(uVar2,uVar6);
    uVar6 = PackedFloatingMUL((ulonglong)(uint)in_stack_00000004[1],uVar7);
    uVar4 = PackedFloatingADD(uVar6,uVar4);
    uVar3 = PackedFloatingADD(uVar2,uVar5);
    *in_stack_00000004 = uVar3;
    *(int *)(in_stack_00000004 + 1) = (int)uVar4;
    FastExitMediaState();
  }
  return (int)in_stack_00000004;
}

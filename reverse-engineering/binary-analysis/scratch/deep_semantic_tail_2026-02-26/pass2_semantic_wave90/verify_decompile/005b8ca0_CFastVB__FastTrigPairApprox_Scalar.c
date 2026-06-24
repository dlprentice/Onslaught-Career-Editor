/* address: 0x005b8ca0 */
/* name: CFastVB__FastTrigPairApprox_Scalar */
/* signature: uint CFastVB__FastTrigPairApprox_Scalar(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

uint CFastVB__FastTrigPairApprox_Scalar(void)

{
  ulonglong in_MM0;
  undefined8 uVar1;
  ulonglong uVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;

  uVar1 = PackedFloatingMUL(in_MM0 & DAT_0065ed9c,(ulonglong)DAT_0065ee50);
  uVar2 = PackedFloatingToIntDwordConv(uVar1,uVar1);
  uVar1 = PackedIntToFloatingDwordConv(uVar2,uVar2);
  uVar1 = PackedFloatingMUL(CONCAT44((int)uVar1,(int)uVar1),DAT_0065ed60);
  uVar4 = PackedFloatingADD(in_MM0 & DAT_0065ed9c,uVar1);
  uVar3 = (undefined4)((ulonglong)uVar1 >> 0x20);
  uVar1 = PackedFloatingADD(uVar4,CONCAT44(uVar3,uVar3));
  uVar1 = CONCAT44((int)uVar1,(int)uVar1);
  if ((uVar2 & 1) != 0) {
    uVar1 = PackedFloatingSUBR(uVar1,DAT_0065ed70);
  }
  uVar4 = PackedFloatingMUL(uVar1,uVar1);
  uVar6 = PackedFloatingMUL(DAT_0065ed68,uVar4);
  uVar5 = PackedFloatingMUL(DAT_0065ed78,uVar4);
  uVar7 = PackedFloatingADD(uVar6,DAT_0065ed18);
  uVar6 = PackedFloatingMUL(DAT_0065ed80,uVar4);
  uVar5 = PackedFloatingMUL(uVar7,uVar5);
  uVar7 = PackedFloatingADD(uVar5,DAT_0065ed18);
  uVar5 = PackedFloatingMUL(DAT_0065ed88,uVar4);
  uVar4 = PackedFloatingMUL(uVar6,uVar7);
  uVar4 = PackedFloatingADD(uVar4,DAT_0065ed18);
  uVar4 = PackedFloatingMUL(uVar4,CONCAT44((int)DAT_0065ed18,(int)uVar5));
  uVar4 = PackedFloatingADD(uVar4,DAT_0065ed18 >> 0x20);
  PackedFloatingMUL(uVar4,CONCAT44((int)uVar1,(int)DAT_0065ed18));
  return (uint)in_MM0 ^ (uint)in_MM0 & 0x80000000;
}

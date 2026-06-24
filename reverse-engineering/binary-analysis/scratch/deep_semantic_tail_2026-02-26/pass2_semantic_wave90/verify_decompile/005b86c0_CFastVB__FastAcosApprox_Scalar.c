/* address: 0x005b86c0 */
/* name: CFastVB__FastAcosApprox_Scalar */
/* signature: int CFastVB__FastAcosApprox_Scalar(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__FastAcosApprox_Scalar(void)

{
  uint uVar1;
  int in_EAX;
  ulonglong in_MM0;
  ulonglong uVar2;
  undefined8 uVar3;
  uint uVar4;
  undefined8 uVar6;
  undefined8 uVar7;
  ulonglong uVar8;
  ulonglong uVar5;

  uVar2 = in_MM0 & DAT_0065ed9c;
  uVar3 = PackedFloatingMUL(uVar2,(ulonglong)DAT_0065edac);
  uVar3 = PackedFloatingSUBR(uVar3,(ulonglong)DAT_0065edac);
  uVar6 = PackedFloatingReciprocalSQRAprox((ulonglong)DAT_0065ed9c,uVar3);
  uVar7 = PackedFloatingMUL(uVar6,uVar6);
  uVar1 = (uint)((int)uVar2 < DAT_0065ede0);
  uVar4 = -uVar1;
  uVar5 = (ulonglong)uVar4;
  uVar7 = PackedFloatingReciprocalSQRIter1(uVar7,uVar3);
  uVar6 = PackedFloatingReciprocalIter2(uVar7,uVar6);
  uVar8 = PackedFloatingMUL(uVar6,uVar3);
  uVar2 = ~uVar5 & uVar8 | uVar2 & uVar4;
  uVar3 = PackedFloatingMUL(uVar2,uVar2);
  uVar7 = PackedFloatingMUL((ulonglong)DAT_0065ede8,uVar3);
  uVar6 = PackedFloatingADD((ulonglong)DAT_0065edf0,uVar3);
  uVar7 = PackedFloatingADD(uVar7,(ulonglong)DAT_0065ede4);
  uVar7 = PackedFloatingMUL(uVar7,uVar3);
  uVar3 = PackedFloatingMUL(uVar3,uVar6);
  uVar3 = PackedFloatingADD(uVar3,(ulonglong)DAT_0065edec);
  uVar7 = PackedFloatingMUL(uVar7,uVar2);
  uVar6 = FloatingReciprocalAprox(uVar6,uVar3);
  uVar3 = PackedFloatingReciprocalIter1(uVar3,uVar6);
  uVar3 = PackedFloatingReciprocalIter2(uVar3,uVar6);
  uVar3 = PackedFloatingMUL(uVar3,uVar7);
  uVar2 = PackedFloatingADD(uVar2,uVar3);
  uVar3 = PackedFloatingADD(~uVar5 & (ulonglong)DAT_0065edf8 ^ DAT_0065ed98 & in_MM0,
                            (ulonglong)DAT_0065edf4);
  uVar2 = PackedFloatingADD(uVar2,~uVar5 & uVar2);
  PackedFloatingADD(uVar3,uVar2 | (ulonglong)(uVar1 * -0x80000000) ^ DAT_0065ed98 & in_MM0);
  return in_EAX;
}

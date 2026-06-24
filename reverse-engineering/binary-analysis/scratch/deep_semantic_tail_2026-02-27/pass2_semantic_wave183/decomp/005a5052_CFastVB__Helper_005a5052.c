/* address: 0x005a5052 */
/* name: CFastVB__Helper_005a5052 */
/* signature: void __stdcall CFastVB__Helper_005a5052(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Helper_005a5052(void *param_1,void *param_2)

{
  undefined4 extraout_MM0_Da;
  ulonglong extraout_MM0;
  undefined8 uVar1;
  ulonglong uVar2;
  undefined4 uVar4;
  undefined8 uVar3;
  undefined8 in_MM4;
  undefined8 uVar5;

  FastExitMediaState();
  uVar1 = *(undefined8 *)param_2;
  uVar2 = *(ulonglong *)((int)param_2 + 8);
  uVar4 = (undefined4)(uVar2 >> 0x20);
  uVar3 = PackedFloatingCompareGE(CONCAT44(uVar4,uVar4),_DAT_005ef188);
  if ((int)uVar3 == 0) {
    CFastVB__FastAcosApprox_Scalar();
    CFastVB__Helper_005b8da0();
    uVar3 = PackedFloatingCompareGE(extraout_MM0 & _DAT_005ef140,DAT_005ef148);
    uVar1 = *(undefined8 *)param_2;
    uVar2 = *(ulonglong *)((int)param_2 + 8);
    if ((int)uVar3 != 0) {
      uVar5 = FloatingReciprocalAprox(in_MM4,extraout_MM0);
      uVar3 = PackedFloatingReciprocalIter1(extraout_MM0,uVar5);
      uVar3 = PackedFloatingReciprocalIter2(uVar3,uVar5);
      uVar3 = PackedFloatingMUL(CONCAT44(extraout_MM0_Da,extraout_MM0_Da),uVar3);
      uVar1 = PackedFloatingMUL(uVar1,uVar3);
      uVar2 = PackedFloatingMUL(uVar2,uVar3);
    }
  }
  uVar2 = uVar2 & _DAT_005ef150;
  *(undefined8 *)param_1 = uVar1;
  *(ulonglong *)((int)param_1 + 8) = uVar2;
  FastExitMediaState();
  return;
}

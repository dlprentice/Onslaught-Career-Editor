/* address: 0x005a4d98 */
/* name: CFastVB__Helper_005a4d98 */
/* signature: void __stdcall CFastVB__Helper_005a4d98(void * param_1, void * param_2, void * param_3, uint param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Helper_005a4d98(void *param_1,void *param_2,void *param_3,uint param_4)

{
  undefined4 uVar1;
  uint extraout_MM0_Da;
  ulonglong extraout_MM0;
  undefined8 extraout_MM0_00;
  undefined8 uVar3;
  ulonglong uVar4;
  undefined8 uVar5;
  uint uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  ulonglong uVar9;
  ulonglong uVar2;

  FastExitMediaState();
  uVar3 = PackedFloatingMUL(*(undefined8 *)param_2,*(undefined8 *)param_3);
  uVar5 = PackedFloatingMUL(*(undefined8 *)((int)param_2 + 8),*(undefined8 *)((int)param_3 + 8));
  uVar3 = PackedFloatingADD(uVar3,uVar5);
  uVar2 = PackedFloatingSUB((ulonglong)DAT_005ef188,(ulonglong)param_4);
  uVar1 = (undefined4)uVar2;
  uVar4 = PackedFloatingAccumulate(uVar3,uVar3);
  uVar9 = PackedFloatingCompareGE(0,uVar4);
  uVar9 = uVar9 & _DAT_005ef1d0;
  uVar4 = uVar4 ^ uVar9;
  uVar5 = PackedFloatingCompareGE(DAT_005ef1e8,uVar4);
  uVar3 = PackedFloatingMUL(uVar4,uVar4);
  uVar3 = PackedFloatingSUBR(uVar3,CONCAT44(_UNK_005ef18c,DAT_005ef188));
  if ((int)uVar5 != 0) {
    uVar7 = PackedFloatingReciprocalSQRAprox((ulonglong)param_4,uVar3);
    uVar5 = PackedFloatingMUL(uVar7,uVar7);
    uVar3 = PackedFloatingReciprocalSQRIter1(uVar3,uVar5);
    uVar4 = PackedFloatingReciprocalIter2(uVar3,uVar7);
    uVar3 = FloatingReciprocalAprox(uVar5,uVar4);
    uVar5 = PackedFloatingReciprocalIter1(uVar4,uVar3);
    PackedFloatingReciprocalIter2(uVar5,uVar3);
    CMeshCollisionVolume__Helper_005b85c0();
    PackedFloatingMUL(extraout_MM0,(ulonglong)param_4);
    CFastVB__Helper_005b8da0();
    PackedFloatingMUL(extraout_MM0 & 0xffffffff,uVar2 & 0xffffffff);
    CFastVB__Helper_005b8da0();
    uVar9 = uVar9 & 0xffffffff;
    uVar3 = PackedFloatingMUL(extraout_MM0_00,uVar4 & 0xffffffff);
    uVar1 = (undefined4)uVar3;
    uVar3 = PackedFloatingMUL((ulonglong)extraout_MM0_Da,uVar4 & 0xffffffff);
    param_4 = (uint)uVar3;
  }
  uVar6 = param_4 ^ (uint)uVar9;
  uVar5 = CONCAT44(uVar6,uVar6);
  uVar3 = PackedFloatingMUL(CONCAT44(uVar1,uVar1),*(undefined8 *)param_2);
  uVar7 = PackedFloatingMUL(uVar5,*(undefined8 *)param_3);
  uVar8 = PackedFloatingMUL(CONCAT44(uVar1,uVar1),*(undefined8 *)((int)param_2 + 8));
  uVar5 = PackedFloatingMUL(uVar5,*(undefined8 *)((int)param_3 + 8));
  uVar3 = PackedFloatingADD(uVar3,uVar7);
  uVar5 = PackedFloatingADD(uVar8,uVar5);
  *(undefined8 *)param_1 = uVar3;
  *(undefined8 *)((int)param_1 + 8) = uVar5;
  FastExitMediaState();
  return;
}

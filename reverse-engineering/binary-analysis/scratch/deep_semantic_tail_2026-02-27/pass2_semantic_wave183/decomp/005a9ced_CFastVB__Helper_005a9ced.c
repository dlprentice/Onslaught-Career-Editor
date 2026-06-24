/* address: 0x005a9ced */
/* name: CFastVB__Helper_005a9ced */
/* signature: int __stdcall CFastVB__Helper_005a9ced(void * param_1, void * param_2, void * param_3) */


int CFastVB__Helper_005a9ced(void *param_1,void *param_2,void *param_3)

{
  undefined4 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;

  FastExitMediaState();
  uVar1 = (undefined4)*(undefined8 *)param_2;
  uVar4 = CONCAT44(uVar1,uVar1);
  uVar1 = (undefined4)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  uVar7 = CONCAT44(uVar1,uVar1);
  uVar8 = CONCAT44(*(undefined4 *)((int)param_2 + 8),*(undefined4 *)((int)param_2 + 8));
  uVar2 = PackedFloatingMUL(uVar4,*(undefined8 *)param_3);
  uVar3 = PackedFloatingMUL(uVar7,*(undefined8 *)((int)param_3 + 0x10));
  uVar5 = PackedFloatingMUL(uVar8,*(undefined8 *)((int)param_3 + 0x20));
  uVar2 = PackedFloatingADD(uVar2,*(undefined8 *)((int)param_3 + 0x30));
  uVar6 = PackedFloatingMUL(uVar4,*(undefined8 *)((int)param_3 + 8));
  uVar4 = PackedFloatingADD(uVar3,uVar5);
  uVar3 = PackedFloatingMUL(uVar7,*(undefined8 *)((int)param_3 + 0x18));
  uVar8 = PackedFloatingMUL(uVar8,*(undefined8 *)((int)param_3 + 0x28));
  uVar7 = PackedFloatingADD(uVar6,*(undefined8 *)((int)param_3 + 0x38));
  uVar4 = PackedFloatingADD(uVar2,uVar4);
  uVar3 = PackedFloatingADD(uVar3,uVar8);
  uVar2 = PackedFloatingADD(uVar7,uVar3);
  uVar1 = (undefined4)((ulonglong)uVar2 >> 0x20);
  uVar8 = CONCAT44(uVar1,uVar1);
  uVar7 = FloatingReciprocalAprox(uVar3,uVar8);
  uVar3 = PackedFloatingReciprocalIter1(uVar8,uVar7);
  uVar7 = PackedFloatingReciprocalIter2(uVar3,uVar7);
  uVar4 = PackedFloatingMUL(uVar4,uVar7);
  uVar2 = PackedFloatingMUL(uVar2,uVar7);
  *(undefined8 *)param_1 = uVar4;
  *(int *)((int)param_1 + 8) = (int)uVar2;
  FastExitMediaState();
  return (int)param_1;
}

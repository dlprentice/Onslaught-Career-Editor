/* address: 0x005a9a5f */
/* name: CFastVB__Helper_005a9a5f */
/* signature: void __stdcall CFastVB__Helper_005a9a5f(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__Helper_005a9a5f(void *param_1,void *param_2)

{
  ulonglong uVar1;
  undefined8 uVar2;
  ulonglong uVar3;
  undefined8 uVar4;
  undefined8 in_MM4;
  undefined8 uVar5;
  ulonglong uVar6;

  FastExitMediaState();
  uVar1 = *(ulonglong *)param_2;
  uVar3 = (ulonglong)*(uint *)((int)param_2 + 8);
  uVar2 = PackedFloatingMUL(uVar1,uVar1);
  uVar4 = PackedFloatingMUL(uVar3,uVar3);
  uVar2 = PackedFloatingADD(uVar2,uVar4);
  uVar2 = PackedFloatingAccumulate(uVar2,uVar2);
  uVar5 = PackedFloatingReciprocalSQRAprox(in_MM4,uVar2);
  uVar6 = PackedFloatingCompareGT(uVar2,_PTR_DAT_005ef170);
  uVar4 = PackedFloatingMUL(uVar5,uVar5);
  uVar2 = PackedFloatingReciprocalSQRIter1(uVar2,uVar4);
  uVar2 = PackedFloatingReciprocalIter2(uVar2,uVar5);
  uVar4 = PackedFloatingMUL(uVar1 & uVar6,uVar2);
  uVar2 = PackedFloatingMUL(uVar3 & uVar6,uVar2);
  *(undefined8 *)param_1 = uVar4;
  *(int *)((int)param_1 + 8) = (int)uVar2;
  FastExitMediaState();
  return;
}

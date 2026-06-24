/* address: 0x005ab00b */
/* name: CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b */
/* signature: void __stdcall CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b(void *param_1,void *param_2)

{
  ulonglong uVar1;
  undefined8 uVar2;
  ulonglong uVar3;
  undefined8 uVar4;
  undefined8 in_MM4;
  undefined8 uVar5;

  uVar1 = *(ulonglong *)param_2;
  uVar3 = *(ulonglong *)((int)param_2 + 8) & _DAT_005ef150;
  uVar2 = PackedFloatingMUL(uVar1,uVar1);
  uVar4 = PackedFloatingMUL(uVar3,uVar3);
  uVar2 = PackedFloatingADD(uVar2,uVar4);
  uVar2 = PackedFloatingAccumulate(uVar2,uVar2);
  uVar5 = PackedFloatingReciprocalSQRAprox(in_MM4,uVar2);
  uVar3 = PackedFloatingCompareGT(uVar2,_PTR_DAT_005ef170);
  uVar4 = PackedFloatingMUL(uVar5,uVar5);
  uVar2 = PackedFloatingReciprocalSQRIter1(uVar2,uVar4);
  uVar2 = PackedFloatingReciprocalIter2(uVar2,uVar5);
  uVar4 = PackedFloatingMUL(uVar1 & uVar3,uVar2);
  uVar2 = PackedFloatingMUL(*(ulonglong *)((int)param_2 + 8) & uVar3,uVar2);
  *(undefined8 *)param_1 = uVar4;
  *(undefined8 *)((int)param_1 + 8) = uVar2;
  FastExitMediaState();
  return;
}

/* address: 0x005a99f8 */
/* name: CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8 */
/* signature: int __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8(void * param_1, void * param_2, void * param_3) */


int CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8
              (void *param_1,void *param_2,void *param_3)

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
  uVar8 = CONCAT44(uVar1,uVar1);
  uVar5 = CONCAT44(*(undefined4 *)((int)param_2 + 8),*(undefined4 *)((int)param_2 + 8));
  uVar2 = PackedFloatingMUL(uVar4,*(undefined8 *)param_3);
  uVar3 = PackedFloatingMUL(uVar8,*(undefined8 *)((int)param_3 + 0x10));
  uVar6 = PackedFloatingMUL(uVar5,*(undefined8 *)((int)param_3 + 0x20));
  uVar7 = PackedFloatingMUL(uVar4,*(undefined8 *)((int)param_3 + 8));
  uVar4 = PackedFloatingADD(uVar3,uVar6);
  uVar8 = PackedFloatingMUL(uVar8,*(undefined8 *)((int)param_3 + 0x18));
  uVar3 = PackedFloatingMUL(uVar5,*(undefined8 *)((int)param_3 + 0x28));
  uVar4 = PackedFloatingADD(uVar2,uVar4);
  uVar2 = PackedFloatingADD(uVar8,uVar3);
  uVar2 = PackedFloatingADD(uVar7,uVar2);
  *(undefined8 *)param_1 = uVar4;
  *(int *)((int)param_1 + 8) = (int)uVar2;
  FastExitMediaState();
  return (int)param_1;
}

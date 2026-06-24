/* address: 0x005aa790 */
/* name: CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790 */
/* signature: int __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790(void * param_1, void * param_2, void * param_3) */


int CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790
              (void *param_1,void *param_2,void *param_3)

{
  undefined4 uVar1;
  undefined8 uVar2;
  undefined4 uVar4;
  undefined8 uVar3;

  FastExitMediaState();
  uVar1 = (undefined4)*(undefined8 *)param_2;
  uVar4 = (undefined4)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  uVar2 = PackedFloatingMUL(CONCAT44(uVar1,uVar1),*(undefined8 *)param_3);
  uVar3 = PackedFloatingMUL(CONCAT44(uVar4,uVar4),*(undefined8 *)((int)param_3 + 0x10));
  uVar2 = PackedFloatingADD(uVar2,uVar3);
  *(undefined8 *)param_1 = uVar2;
  FastExitMediaState();
  return (int)param_1;
}

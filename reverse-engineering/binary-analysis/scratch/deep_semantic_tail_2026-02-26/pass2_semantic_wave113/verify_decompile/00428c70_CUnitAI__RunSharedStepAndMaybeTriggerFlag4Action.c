/* address: 0x00428c70 */
/* name: CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action */
/* signature: void __fastcall CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action(void * param_1) */


void __fastcall CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action(void *param_1)

{
  CUnit__Helper_00402010((int)param_1);
  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}

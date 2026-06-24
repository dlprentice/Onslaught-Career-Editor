/* address: 0x004d20a0 */
/* name: CExplosionInitThing__UpdateAndTriggerDeferredStart_NoUnitAIPrepass */
/* signature: void __fastcall CExplosionInitThing__UpdateAndTriggerDeferredStart_NoUnitAIPrepass(void * param_1) */


void __fastcall CExplosionInitThing__UpdateAndTriggerDeferredStart_NoUnitAIPrepass(void *param_1)

{
  CExplosionInitThing__UpdateAndTriggerDeferredStart(param_1);
  if (*(int *)(*(int *)((int)param_1 + 0x164) + 0x11c) == 0) {
    CExplosionInitThing__ctor_like_004fd230(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}

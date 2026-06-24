/* address: 0x0047bf60 */
/* name: CUnitAI__Unk_0047bf60 */
/* signature: void __fastcall CUnitAI__Unk_0047bf60(void * param_1) */


void __fastcall CUnitAI__Unk_0047bf60(void *param_1)

{
  CUnitAI__Helper_00403760(param_1);
  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x11c) == 0) &&
     (*(int *)(*(int *)((int)param_1 + 0x164) + 0x124) == 0)) {
    CExplosionInitThing__ctor_like_004fd230(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}

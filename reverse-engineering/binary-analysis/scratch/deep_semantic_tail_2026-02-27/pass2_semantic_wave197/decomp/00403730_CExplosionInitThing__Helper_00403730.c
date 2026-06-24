/* address: 0x00403730 */
/* name: CExplosionInitThing__Helper_00403730 */
/* signature: void __fastcall CExplosionInitThing__Helper_00403730(void * param_1) */


void __fastcall CExplosionInitThing__Helper_00403730(void *param_1)

{
  CUnitAI__Helper_00402000((int)param_1);
  if (((*(byte *)((int)param_1 + 0x2c) & 4) != 0) &&
     (*(int *)(*(int *)((int)param_1 + 0x164) + 0x11c) == 0)) {
    CExplosionInitThing__ctor_like_004fd230(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}

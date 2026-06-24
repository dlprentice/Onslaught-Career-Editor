/* address: 0x00403760 */
/* name: CUnitAI__Helper_00403760 */
/* signature: void __fastcall CUnitAI__Helper_00403760(void * param_1) */


void __fastcall CUnitAI__Helper_00403760(void *param_1)

{
  CUnit__Helper_00402010((int)param_1);
  if ((((*(byte *)((int)param_1 + 0x2c) & 4) != 0) &&
      (*(int *)(*(int *)((int)param_1 + 0x164) + 0x11c) == 0)) &&
     (*(int *)(*(int *)((int)param_1 + 0x164) + 0x124) == 0)) {
    CExplosionInitThing__ctor_like_004fd230(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
  }
  return;
}

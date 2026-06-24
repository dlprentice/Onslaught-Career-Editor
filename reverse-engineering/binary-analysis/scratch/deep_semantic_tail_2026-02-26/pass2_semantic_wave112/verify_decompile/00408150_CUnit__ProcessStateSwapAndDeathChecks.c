/* address: 0x00408150 */
/* name: CUnit__ProcessStateSwapAndDeathChecks */
/* signature: void __fastcall CUnit__ProcessStateSwapAndDeathChecks(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__ProcessStateSwapAndDeathChecks(void *param_1)

{
  CBattleEngine__Unk_00406460((int)param_1);
  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    CGeneralVolume__SpawnPickupAndDispatch(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
    CUnit__Helper_00402010((int)param_1);
    return;
  }
  if ((_DAT_005d8bf0 < *(float *)((int)param_1 + 0x24) - DAT_006fbdfc) &&
     ((*(int *)((int)param_1 + 0x15c) != 0 || (DAT_00662dd0 == 0)))) {
    (**(code **)(*(int *)param_1 + 200))();
  }
  CUnit__Helper_00402010((int)param_1);
  return;
}

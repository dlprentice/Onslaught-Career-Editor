/* address: 0x00408150 */
/* name: CUnit__Unk_00408150 */
/* signature: void __fastcall CUnit__Unk_00408150(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__Unk_00408150(void *param_1)

{
  CBattleEngine__Unk_00406460((int)param_1);
  if ((*(byte *)((int)param_1 + 0x2c) & 4) != 0) {
    CGeneralVolume__Unk_0040dfb0(param_1);
    (**(code **)(*(int *)param_1 + 0x38))();
    CUnit__Unk_00402010((int)param_1);
    return;
  }
  if ((_DAT_005d8bf0 < *(float *)((int)param_1 + 0x24) - DAT_006fbdfc) &&
     ((*(int *)((int)param_1 + 0x15c) != 0 || (DAT_00662dd0 == 0)))) {
    (**(code **)(*(int *)param_1 + 200))();
  }
  CUnit__Unk_00402010((int)param_1);
  return;
}

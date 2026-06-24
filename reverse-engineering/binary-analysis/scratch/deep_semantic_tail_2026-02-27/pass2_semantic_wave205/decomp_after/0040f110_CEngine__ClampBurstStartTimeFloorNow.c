/* address: 0x0040f110 */
/* name: CEngine__ClampBurstStartTimeFloorNow */
/* signature: void __fastcall CEngine__ClampBurstStartTimeFloorNow(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CEngine__ClampBurstStartTimeFloorNow(int param_1)

{
  if (*(float *)(param_1 + 0x60c) + _DAT_005d85bc < DAT_00672fd0) {
    *(float *)(param_1 + 0x60c) = DAT_00672fd0;
  }
  return;
}

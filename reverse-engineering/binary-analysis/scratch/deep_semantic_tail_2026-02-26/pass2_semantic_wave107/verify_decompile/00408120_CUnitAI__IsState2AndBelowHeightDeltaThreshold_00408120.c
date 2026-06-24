/* address: 0x00408120 */
/* name: CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120 */
/* signature: int __fastcall CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120(int param_1)

{
  if ((*(int *)(param_1 + 0x260) == 2) &&
     (DAT_00672fd0 - *(float *)(param_1 + 0xcc) < _DAT_005d85ec)) {
    return 1;
  }
  return 0;
}

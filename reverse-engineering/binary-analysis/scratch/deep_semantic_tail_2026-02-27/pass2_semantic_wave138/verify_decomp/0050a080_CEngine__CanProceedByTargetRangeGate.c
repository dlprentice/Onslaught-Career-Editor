/* address: 0x0050a080 */
/* name: CEngine__CanProceedByTargetRangeGate */
/* signature: int __fastcall CEngine__CanProceedByTargetRangeGate(int param_1) */


int __fastcall CEngine__CanProceedByTargetRangeGate(int param_1)

{
  if ((*(int *)(param_1 + 0xa0) != 0) && (DAT_00672fd0 <= *(float *)(param_1 + 100))) {
    return 0;
  }
  return 1;
}

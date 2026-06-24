/* address: 0x0040c5b0 */
/* name: CRepairPadAI__IsWithinRepairBounds */
/* signature: int __fastcall CRepairPadAI__IsWithinRepairBounds(int param_1) */


int __fastcall CRepairPadAI__IsWithinRepairBounds(int param_1)

{
  if ((*(float *)(*(int *)(param_1 + 0x4b0) + 0x20) <= *(float *)(param_1 + 0xfc)) &&
     (*(float *)(*(int *)(param_1 + 0x4b0) + 0x1c) <= *(float *)(param_1 + 0xf8))) {
    return 1;
  }
  return 0;
}

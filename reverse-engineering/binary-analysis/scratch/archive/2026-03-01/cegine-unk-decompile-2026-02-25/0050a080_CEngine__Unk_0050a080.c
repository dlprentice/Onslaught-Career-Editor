/* address: 0x0050a080 */
/* name: CEngine__Unk_0050a080 */
/* signature: int __fastcall CEngine__Unk_0050a080(int param_1) */


int __fastcall CEngine__Unk_0050a080(int param_1)

{
  if ((*(int *)(param_1 + 0xa0) != 0) && (DAT_00672fd0 <= *(float *)(param_1 + 100))) {
    return 0;
  }
  return 1;
}

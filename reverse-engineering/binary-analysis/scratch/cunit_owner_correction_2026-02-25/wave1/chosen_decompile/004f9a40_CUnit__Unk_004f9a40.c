/* address: 0x004f9a40 */
/* name: CUnit__Unk_004f9a40 */
/* signature: double __fastcall CUnit__Unk_004f9a40(int param_1) */


double __fastcall CUnit__Unk_004f9a40(int param_1)

{
  double dVar1;

  if (*(int *)(param_1 + 0x178) == 0) {
    return (double)*(float *)(param_1 + 0xf8);
  }
  dVar1 = CDestroyableSegment__Unk_00444370(*(int *)(param_1 + 0x178));
  return dVar1;
}

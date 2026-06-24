/* address: 0x004f99f0 */
/* name: CDXCompass__Helper_004f99f0 */
/* signature: double __fastcall CDXCompass__Helper_004f99f0(int param_1) */


double __fastcall CDXCompass__Helper_004f99f0(int param_1)

{
  double dVar1;

  if (*(int *)(param_1 + 0x178) != 0) {
    dVar1 = CDestroyableSegment__Unk_00444330(*(int *)(param_1 + 0x178));
    return dVar1;
  }
  return (double)*(float *)(param_1 + 0xf8);
}

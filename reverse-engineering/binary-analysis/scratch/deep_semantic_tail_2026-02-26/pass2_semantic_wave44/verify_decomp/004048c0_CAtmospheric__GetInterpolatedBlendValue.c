/* address: 0x004048c0 */
/* name: CAtmospheric__GetInterpolatedBlendValue */
/* signature: double __fastcall CAtmospheric__GetInterpolatedBlendValue(int param_1) */


double __fastcall CAtmospheric__GetInterpolatedBlendValue(int param_1)

{
  if (*(float *)(param_1 + 8) < *(float *)(param_1 + 0xc)) {
    return (double)*(float *)(param_1 + 8);
  }
  return (double)((*(float *)(param_1 + 8) - *(float *)(param_1 + 0xc)) * DAT_008a9e44 +
                 *(float *)(param_1 + 0xc));
}

/* address: 0x00594ef8 */
/* name: CDXTexture__SetDecodeOptionFloat */
/* signature: void __stdcall CDXTexture__SetDecodeOptionFloat(int param_1, int param_2, double param_3) */


void CDXTexture__SetDecodeOptionFloat(int param_1,int param_2,double param_3)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    *(uint *)(param_2 + 8) = *(uint *)(param_2 + 8) | 1;
    *(float *)(param_2 + 0x28) = (float)param_3;
  }
  return;
}

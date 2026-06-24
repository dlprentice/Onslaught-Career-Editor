/* address: 0x005b1c30 */
/* name: CDXTexture__Helper_005b1c30 */
/* signature: void __stdcall CDXTexture__Helper_005b1c30(int param_1, int param_2) */


void CDXTexture__Helper_005b1c30(int param_1,int param_2)

{
  if (param_2 != 0) {
    CRT__FreeBase(param_2 - (uint)*(byte *)(param_2 + -1));
  }
  return;
}

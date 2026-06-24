/* address: 0x0059ccb3 */
/* name: CDXTexture__FreeDecodeStateIfOwnerPresent */
/* signature: void __stdcall CDXTexture__FreeDecodeStateIfOwnerPresent(int param_1, int param_2) */


void CDXTexture__FreeDecodeStateIfOwnerPresent(int param_1,int param_2)

{
  if ((param_1 != 0) && (param_2 != 0)) {
    CRT__FreeBase(param_2);
  }
  return;
}

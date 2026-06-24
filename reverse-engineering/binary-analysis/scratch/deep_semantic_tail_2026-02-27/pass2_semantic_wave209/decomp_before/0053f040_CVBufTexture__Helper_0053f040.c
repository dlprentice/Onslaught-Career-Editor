/* address: 0x0053f040 */
/* name: CVBufTexture__Helper_0053f040 */
/* signature: void __stdcall CVBufTexture__Helper_0053f040(int param_1) */


void CVBufTexture__Helper_0053f040(int param_1)

{
  if ((char)param_1 != '\0') {
    D3DStateCache__ForceSlotMode4or5(0);
    return;
  }
  D3DStateCache__SetStateCached(0,1,4);
  return;
}

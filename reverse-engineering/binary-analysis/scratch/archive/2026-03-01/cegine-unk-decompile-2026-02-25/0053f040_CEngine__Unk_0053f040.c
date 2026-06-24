/* address: 0x0053f040 */
/* name: CEngine__Unk_0053f040 */
/* signature: void __stdcall CEngine__Unk_0053f040(int param_1) */


void CEngine__Unk_0053f040(int param_1)

{
  if ((char)param_1 != '\0') {
    D3DStateCache__ForceSlotMode4or5(0);
    return;
  }
  D3DStateCache__SetStateCached(0,1,4);
  return;
}

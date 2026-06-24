/* address: 0x00592d29 */
/* name: CTexture__SetDecodeContextTriplet */
/* signature: void __stdcall CTexture__SetDecodeContextTriplet(int param_1, int param_2, int param_3, int param_4) */


void CTexture__SetDecodeContextTriplet(int param_1,int param_2,int param_3,int param_4)

{
  *(int *)(param_1 + 0x48) = param_2;
  *(int *)(param_1 + 0x40) = param_3;
  *(int *)(param_1 + 0x44) = param_4;
  return;
}

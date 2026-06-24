/* address: 0x00592d63 */
/* name: CDXTexture__ReportDecodeWarning */
/* signature: void __stdcall CDXTexture__ReportDecodeWarning(int param_1, int param_2) */


void CDXTexture__ReportDecodeWarning(int param_1,int param_2)

{
  if (*(code **)(param_1 + 0x44) != (code *)0x0) {
    (**(code **)(param_1 + 0x44))(param_1,param_2);
  }
  return;
}

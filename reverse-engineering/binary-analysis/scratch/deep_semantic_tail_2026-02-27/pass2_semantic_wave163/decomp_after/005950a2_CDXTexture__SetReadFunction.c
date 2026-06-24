/* address: 0x005950a2 */
/* name: CDXTexture__SetReadFunction */
/* signature: void __stdcall CDXTexture__SetReadFunction(int param_1, int param_2, int param_3) */


void CDXTexture__SetReadFunction(int param_1,int param_2,int param_3)

{
  *(int *)(param_1 + 0x54) = param_2;
  *(int *)(param_1 + 0x50) = param_3;
  if (*(int *)(param_1 + 0x4c) != 0) {
    *(undefined4 *)(param_1 + 0x4c) = 0;
    CDXTexture__ReportDecodeWarning(param_1,0x5eeb88);
    CDXTexture__ReportDecodeWarning(param_1,0x5eeb54);
  }
  *(undefined4 *)(param_1 + 0x120) = 0;
  return;
}

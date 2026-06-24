/* address: 0x00561679 */
/* name: CDXTexture__Helper_00561679 */
/* signature: void __fastcall CDXTexture__Helper_00561679(int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXTexture__Helper_00561679(int param_1,int param_2)

{
  ushort in_FPUStatusWord;
  float10 in_ST0;
  ushort unaff_retaddr;
  uint uStack_4;

  uStack_4 = (uint)((ulonglong)(double)in_ST0 >> 0x20);
  if (((ulonglong)(double)in_ST0 & 0x7ff0000000000000) == 0) {
    fscale(in_ST0,(float10)_DAT_005e5c1c);
  }
  else if ((uStack_4 & 0x7ff00000) == 0x7ff00000) {
    fscale(in_ST0,(float10)_DAT_005e5c14);
  }
  else if (((unaff_retaddr == 0x27f) || ((unaff_retaddr & 0x20) != 0)) ||
          ((in_FPUStatusWord & 0x20) == 0)) {
    return;
  }
  if (param_2 == 0x1d) {
    CRT__ReportMathErrorAndRestoreControlWord_00561530();
    return;
  }
  __startOneArgErrorHandling();
  return;
}

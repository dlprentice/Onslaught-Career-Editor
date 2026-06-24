/* address: 0x00592d9e */
/* name: CDXTexture__WarnPngChunkWithFormattedTag */
/* signature: void __stdcall CDXTexture__WarnPngChunkWithFormattedTag(int param_1, int param_2) */


void CDXTexture__WarnPngChunkWithFormattedTag(int param_1,int param_2)

{
  void *in_stack_ffffffac;

  CDXTexture__FormatChunkTagForDiagnostics(&stack0xffffffac,param_1,param_2,in_stack_ffffffac);
  CDXTexture__ReportDecodeWarning(param_1,(int)&stack0xffffffac);
  return;
}

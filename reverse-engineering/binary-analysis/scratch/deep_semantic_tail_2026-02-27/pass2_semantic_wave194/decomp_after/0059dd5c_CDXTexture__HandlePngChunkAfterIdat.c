/* address: 0x0059dd5c */
/* name: CDXTexture__HandlePngChunkAfterIdat */
/* signature: void __stdcall CDXTexture__HandlePngChunkAfterIdat(void * param_1, int param_2, uint param_3) */


void CDXTexture__HandlePngChunkAfterIdat(void *param_1,int param_2,uint param_3)

{
  CDXTexture__ValidateChunkTagAsciiOrLog(param_1,(byte *)((int)param_1 + 0x10c));
  if (((*(byte *)((int)param_1 + 0x10c) & 0x20) == 0) &&
     (CDXTexture__LogChunkTagDiagnostic(param_1,0x5f3e78), param_2 == 0)) {
    return;
  }
  if ((*(uint *)((int)param_1 + 0x58) & 4) != 0) {
    *(uint *)((int)param_1 + 0x58) = *(uint *)((int)param_1 + 0x58) | 8;
  }
  CDXTexture__FinalizePngChunkAndVerifyCrc(param_1,param_3);
  return;
}

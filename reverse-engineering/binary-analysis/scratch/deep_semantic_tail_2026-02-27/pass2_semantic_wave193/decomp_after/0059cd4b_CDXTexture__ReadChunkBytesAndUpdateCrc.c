/* address: 0x0059cd4b */
/* name: CDXTexture__ReadChunkBytesAndUpdateCrc */
/* signature: void __stdcall CDXTexture__ReadChunkBytesAndUpdateCrc(void * param_1, int param_2, int param_3) */


void CDXTexture__ReadChunkBytesAndUpdateCrc(void *param_1,int param_2,int param_3)

{
  CDXTexture__ReadFromSource(param_1,param_2,param_3);
  CDXTexture__UpdateChunkCrc((int)param_1,param_2,param_3);
  return;
}

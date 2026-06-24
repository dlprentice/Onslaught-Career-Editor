/* address: 0x0059cd4b */
/* name: CTexture__Helper_0059cd4b */
/* signature: void __stdcall CTexture__Helper_0059cd4b(void * param_1, int param_2, int param_3) */


void CTexture__Helper_0059cd4b(void *param_1,int param_2,int param_3)

{
  CDXTexture__ReadFromSource(param_1,param_2,param_3);
  CDXTexture__UpdateChunkCrc((int)param_1,param_2,param_3);
  return;
}

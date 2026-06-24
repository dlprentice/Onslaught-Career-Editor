/* address: 0x005b1c50 */
/* name: CDXTexture__GetBufferTailAvailable */
/* signature: int __stdcall CDXTexture__GetBufferTailAvailable(int param_1, int param_2, int param_3, int param_4) */


int CDXTexture__GetBufferTailAvailable(int param_1,int param_2,int param_3,int param_4)

{
  return *(int *)(*(int *)(param_1 + 4) + 0x2c) - param_4;
}

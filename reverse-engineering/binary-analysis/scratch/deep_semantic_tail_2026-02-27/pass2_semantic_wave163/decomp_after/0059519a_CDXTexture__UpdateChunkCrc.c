/* address: 0x0059519a */
/* name: CDXTexture__UpdateChunkCrc */
/* signature: void __stdcall CDXTexture__UpdateChunkCrc(int param_1, int param_2, int param_3) */


void CDXTexture__UpdateChunkCrc(int param_1,int param_2,int param_3)

{
  uint uVar1;

  if ((*(byte *)(param_1 + 0x10c) & 0x20) == 0) {
    if ((*(byte *)(param_1 + 0x5d) & 8) != 0) {
      return;
    }
  }
  else if ((*(uint *)(param_1 + 0x5c) & 0x300) == 0x300) {
    return;
  }
  uVar1 = CDXTexture__Crc32_Update(*(uint *)(param_1 + 0x100),(void *)param_2,param_3);
  *(uint *)(param_1 + 0x100) = uVar1;
  return;
}

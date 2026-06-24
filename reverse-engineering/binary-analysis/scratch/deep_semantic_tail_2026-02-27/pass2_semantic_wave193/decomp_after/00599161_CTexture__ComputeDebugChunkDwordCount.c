/* address: 0x00599161 */
/* name: CTexture__ComputeDebugChunkDwordCount */
/* signature: int __fastcall CTexture__ComputeDebugChunkDwordCount(int param_1) */


int __fastcall CTexture__ComputeDebugChunkDwordCount(int param_1)

{
  return (*(int *)(param_1 + 4) + 3U >> 2) + 2;
}

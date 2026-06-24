/* address: 0x0059c750 */
/* name: CDXTexture__BeginAsyncDecodeJob */
/* signature: int __stdcall CDXTexture__BeginAsyncDecodeJob(int param_1) */


int CDXTexture__BeginAsyncDecodeJob(int param_1)

{
  uint *puVar1;
  int iVar2;

  if ((param_1 == 0) || (puVar1 = *(uint **)(param_1 + 0x1c), puVar1 == (uint *)0x0)) {
    iVar2 = -2;
  }
  else {
    *(undefined4 *)(param_1 + 0x14) = 0;
    *(undefined4 *)(param_1 + 8) = 0;
    *(undefined4 *)(param_1 + 0x18) = 0;
    *puVar1 = -(uint)(puVar1[3] != 0) & 7;
    CDXTexture__Helper_005b1db0(*(void **)(*(int *)(param_1 + 0x1c) + 0x14),param_1,(void *)0x0);
    iVar2 = 0;
  }
  return iVar2;
}

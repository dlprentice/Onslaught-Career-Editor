/* address: 0x005937c7 */
/* name: CDXTexture__EnableSwap16TransformIfNeeded */
/* signature: void __stdcall CDXTexture__EnableSwap16TransformIfNeeded(int param_1) */


void CDXTexture__EnableSwap16TransformIfNeeded(int param_1)

{
  if (*(char *)(param_1 + 0x117) == '\x10') {
    *(uint *)(param_1 + 0x60) = *(uint *)(param_1 + 0x60) | 0x10;
  }
  return;
}

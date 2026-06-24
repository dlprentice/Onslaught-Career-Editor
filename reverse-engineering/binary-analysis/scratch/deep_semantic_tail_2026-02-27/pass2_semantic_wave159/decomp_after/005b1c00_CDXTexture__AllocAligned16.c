/* address: 0x005b1c00 */
/* name: CDXTexture__AllocAligned16 */
/* signature: void __stdcall CDXTexture__AllocAligned16(int param_1, int param_2) */


void CDXTexture__AllocAligned16(int param_1,int param_2)

{
  void *pvVar1;
  uint uVar2;

  pvVar1 = _malloc(param_2 + 0x10);
  if (pvVar1 == (void *)0x0) {
    return;
  }
  uVar2 = (int)pvVar1 + 0x10U & 0xfffffff0;
  *(char *)(uVar2 - 1) = (char)uVar2 - (char)pvVar1;
  return;
}

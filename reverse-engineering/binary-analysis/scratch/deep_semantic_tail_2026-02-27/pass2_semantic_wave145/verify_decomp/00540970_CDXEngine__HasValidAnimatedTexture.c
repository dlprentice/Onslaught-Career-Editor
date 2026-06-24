/* address: 0x00540970 */
/* name: CDXEngine__HasValidAnimatedTexture */
/* signature: int __fastcall CDXEngine__HasValidAnimatedTexture(int param_1) */


int __fastcall CDXEngine__HasValidAnimatedTexture(int param_1)

{
  void *pvVar1;

  if (*(void **)(param_1 + 0x170) != (void *)0x0) {
    pvVar1 = CDXTexture__GetAnimatedFrame(*(void **)(param_1 + 0x170));
    if (pvVar1 != (void *)0x0) {
      return 1;
    }
  }
  return 0;
}

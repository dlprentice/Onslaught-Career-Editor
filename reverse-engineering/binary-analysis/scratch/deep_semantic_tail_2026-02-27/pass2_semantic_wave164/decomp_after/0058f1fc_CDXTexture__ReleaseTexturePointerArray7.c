/* address: 0x0058f1fc */
/* name: CDXTexture__ReleaseTexturePointerArray7 */
/* signature: void __fastcall CDXTexture__ReleaseTexturePointerArray7(int param_1) */


void __fastcall CDXTexture__ReleaseTexturePointerArray7(int param_1)

{
  void *this;
  uint uVar1;
  int unaff_EDI;

  uVar1 = 0;
  do {
    this = *(void **)(param_1 + uVar1 * 4);
    if (this != (void *)0x0) {
      CTexture__Dtor_ReleaseBindings_DeleteOnFlag(this,(void *)0x1,unaff_EDI);
    }
    uVar1 = uVar1 + 1;
  } while (uVar1 < 7);
  return;
}

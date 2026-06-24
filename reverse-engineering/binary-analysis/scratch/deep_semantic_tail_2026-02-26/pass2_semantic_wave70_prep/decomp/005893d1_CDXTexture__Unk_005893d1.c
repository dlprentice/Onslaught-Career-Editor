/* address: 0x005893d1 */
/* name: CDXTexture__Unk_005893d1 */
/* signature: void __fastcall CDXTexture__Unk_005893d1(int param_1) */


void __fastcall CDXTexture__Unk_005893d1(int param_1)

{
  void *ptr;

  ptr = *(void **)(param_1 + 0xc);
  if (ptr != (void *)0x0) {
    CDXTexture__Unk_005893d1((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  return;
}

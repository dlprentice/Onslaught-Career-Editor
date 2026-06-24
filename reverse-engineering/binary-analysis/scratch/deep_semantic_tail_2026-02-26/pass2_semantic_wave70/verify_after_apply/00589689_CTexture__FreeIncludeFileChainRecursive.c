/* address: 0x00589689 */
/* name: CTexture__FreeIncludeFileChainRecursive */
/* signature: void __fastcall CTexture__FreeIncludeFileChainRecursive(int param_1) */


void __fastcall CTexture__FreeIncludeFileChainRecursive(int param_1)

{
  void *ptr;

  ptr = *(void **)(param_1 + 4);
  if (ptr != (void *)0x0) {
    CTexture__FreeIncludeFileChainRecursive((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  return;
}

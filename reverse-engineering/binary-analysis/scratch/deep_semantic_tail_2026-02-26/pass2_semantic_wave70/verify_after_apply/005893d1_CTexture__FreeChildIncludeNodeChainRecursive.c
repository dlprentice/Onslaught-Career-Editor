/* address: 0x005893d1 */
/* name: CTexture__FreeChildIncludeNodeChainRecursive */
/* signature: void __fastcall CTexture__FreeChildIncludeNodeChainRecursive(int param_1) */


void __fastcall CTexture__FreeChildIncludeNodeChainRecursive(int param_1)

{
  void *ptr;

  ptr = *(void **)(param_1 + 0xc);
  if (ptr != (void *)0x0) {
    CTexture__FreeChildIncludeNodeChainRecursive((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  return;
}

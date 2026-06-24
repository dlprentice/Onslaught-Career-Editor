/* address: 0x00589367 */
/* name: CTexture__ReleaseIncludeNodeTreeRecursive */
/* signature: void __fastcall CTexture__ReleaseIncludeNodeTreeRecursive(int param_1) */


void __fastcall CTexture__ReleaseIncludeNodeTreeRecursive(int param_1)

{
  void *ptr;

  if (*(undefined4 **)(param_1 + 4) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 4))(1);
  }
  if (*(undefined4 **)(param_1 + 8) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 8))(1);
  }
  ptr = *(void **)(param_1 + 0xc);
  if (ptr != (void *)0x0) {
    CTexture__ReleaseIncludeNodeTreeRecursive((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  return;
}

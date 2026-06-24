/* address: 0x00589689 */
/* name: CFastVB__Unk_00589689 */
/* signature: void __fastcall CFastVB__Unk_00589689(int param_1) */


void __fastcall CFastVB__Unk_00589689(int param_1)

{
  void *ptr;

  ptr = *(void **)(param_1 + 4);
  if (ptr != (void *)0x0) {
    CFastVB__Unk_00589689((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  return;
}

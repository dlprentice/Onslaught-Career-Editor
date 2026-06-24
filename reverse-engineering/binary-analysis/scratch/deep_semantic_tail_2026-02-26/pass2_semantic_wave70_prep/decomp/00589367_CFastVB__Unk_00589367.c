/* address: 0x00589367 */
/* name: CFastVB__Unk_00589367 */
/* signature: void __fastcall CFastVB__Unk_00589367(int param_1) */


void __fastcall CFastVB__Unk_00589367(int param_1)

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
    CFastVB__Unk_00589367((int)ptr);
    OID__FreeObject_Callback(ptr);
  }
  return;
}

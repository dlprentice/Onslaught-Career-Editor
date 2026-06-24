/* address: 0x0048afb0 */
/* name: CUnitAI__Unk_0048afb0 */
/* signature: void __fastcall CUnitAI__Unk_0048afb0(int param_1) */


void __fastcall CUnitAI__Unk_0048afb0(int param_1)

{
  undefined4 *puVar1;
  int *value;
  void *value_00;

  while( true ) {
    puVar1 = *(undefined4 **)(param_1 + 8);
    *(undefined4 **)(param_1 + 0x10) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (value = (int *)*puVar1, value == (int *)0x0)) break;
    CSPtrSet__Remove((int *)(param_1 + 8),value);
    (**(code **)(*value + 8))();
  }
  while( true ) {
    puVar1 = *(undefined4 **)(param_1 + 0x18);
    *(undefined4 **)(param_1 + 0x20) = puVar1;
    if ((puVar1 == (undefined4 *)0x0) || (value_00 = (void *)*puVar1, value_00 == (void *)0x0))
    break;
    CSPtrSet__Remove((int *)(param_1 + 0x18),value_00);
    OID__FreeObject(value_00);
  }
  return;
}

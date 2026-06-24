/* address: 0x004fcfa0 */
/* name: CUnit__Unk_004fcfa0 */
/* signature: void __fastcall CUnit__Unk_004fcfa0(int param_1) */


void __fastcall CUnit__Unk_004fcfa0(int param_1)

{
  undefined4 *puVar1;
  int *value;

  CGenericActiveReader__SetReader((void *)(param_1 + 0x144),(void *)0x0);
  while ((puVar1 = *(undefined4 **)(param_1 + 0x18c), puVar1 != (undefined4 *)0x0 &&
         (value = (int *)*puVar1, value != (int *)0x0))) {
    CSPtrSet__Remove((int *)(param_1 + 0x18c),value);
    (**(code **)(*value + 8))();
  }
  return;
}

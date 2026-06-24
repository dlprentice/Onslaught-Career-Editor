/* address: 0x0047e8a0 */
/* name: CUnitAI__Unk_0047e8a0 */
/* signature: void __fastcall CUnitAI__Unk_0047e8a0(int param_1) */


void __fastcall CUnitAI__Unk_0047e8a0(int param_1)

{
  if (*(void **)(param_1 + 0x24) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x24));
    *(undefined4 *)(param_1 + 0x24) = 0;
  }
  if (*(void **)(param_1 + 0x1028) != (void *)0x0) {
    OID__FreeObject(*(void **)(param_1 + 0x1028));
    *(undefined4 *)(param_1 + 0x1028) = 0;
  }
  return;
}

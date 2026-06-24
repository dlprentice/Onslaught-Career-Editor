/* address: 0x00481400 */
/* name: CUnitAI__Unk_00481400 */
/* signature: int __fastcall CUnitAI__Unk_00481400(int param_1) */


int __fastcall CUnitAI__Unk_00481400(int param_1)

{
  int iVar1;
  undefined4 *puVar2;

  eh_vector_constructor_iterator
            ((void *)(param_1 + 0x9c),4,2,CGenericActiveReader__ctor_Zero,CGenericActiveReader__dtor
            );
  *(undefined4 *)(param_1 + 0x5c) = 0;
  *(undefined4 *)(param_1 + 0x1fc) = 0;
  *(undefined4 *)(param_1 + 0x200) = 0;
  *(undefined4 *)(param_1 + 0x60) = 0;
  puVar2 = (undefined4 *)(param_1 + 0x34);
  for (iVar1 = 6; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 1;
    puVar2 = puVar2 + 1;
  }
  return param_1;
}

/* address: 0x0047e870 */
/* name: CUnitAI__Unk_0047e870 */
/* signature: int __fastcall CUnitAI__Unk_0047e870(int param_1) */


int __fastcall CUnitAI__Unk_0047e870(int param_1)

{
  int iVar1;
  undefined4 *puVar2;

  *(undefined4 *)(param_1 + 0x20) = 0;
  *(undefined4 *)(param_1 + 0x24) = 0;
  puVar2 = (undefined4 *)(param_1 + 0x28);
  for (iVar1 = 0x400; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined4 *)(param_1 + 0x1028) = 0;
  return param_1;
}

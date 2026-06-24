/* address: 0x00440c40 */
/* name: CDamage__Unk_00440c40 */
/* signature: void __fastcall CDamage__Unk_00440c40(void * param_1) */


void __fastcall CDamage__Unk_00440c40(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;

  puVar2 = param_1;
  for (iVar1 = 20000; puVar2 = puVar2 + 1, iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
  }
  puVar2 = (undefined4 *)((int)param_1 + 0x13884);
  for (iVar1 = 0x800; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x15888) = 1;
  *(undefined4 *)((int)param_1 + 0x15884) = 1;
  return;
}

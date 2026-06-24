/* address: 0x00598d6b */
/* name: CFastVB__InitNodeType13 */
/* signature: int __fastcall CFastVB__InitNodeType13(void * param_1) */


int __fastcall CFastVB__InitNodeType13(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;

  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(undefined4 *)((int)param_1 + 4) = 0xd;
  *(undefined ***)param_1 = &PTR_CTexture__Unk_00598fc0_005ef270;
  *(undefined4 *)((int)param_1 + 0x10) = 0;
  *(undefined4 *)((int)param_1 + 0x14) = 0;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  puVar2 = (undefined4 *)((int)param_1 + 0x20);
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x10) = 3;
  return (int)param_1;
}

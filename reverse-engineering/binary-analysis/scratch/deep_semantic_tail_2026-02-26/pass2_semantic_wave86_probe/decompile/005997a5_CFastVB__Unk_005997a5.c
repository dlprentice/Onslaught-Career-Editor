/* address: 0x005997a5 */
/* name: CFastVB__Unk_005997a5 */
/* signature: int __fastcall CFastVB__Unk_005997a5(void * param_1) */


int __fastcall CFastVB__Unk_005997a5(void *param_1)

{
  int iVar1;
  int unaff_EDI;
  undefined4 *puVar2;

  CTexture__Helper_00598702(param_1,(void *)0x11,unaff_EDI);
  *(undefined4 *)((int)param_1 + 0x30) = 0;
  *(undefined4 *)((int)param_1 + 0x34) = 0;
  *(undefined4 *)((int)param_1 + 0x38) = 0;
  *(undefined4 *)((int)param_1 + 0x3c) = 0;
  *(undefined4 *)((int)param_1 + 0x40) = 0;
  *(undefined4 *)((int)param_1 + 0x54) = 0;
  *(undefined4 *)((int)param_1 + 0x58) = 0;
  *(undefined ***)param_1 = &PTR_CTexture__Unk_00599a3c_005ef374;
  puVar2 = (undefined4 *)((int)param_1 + 0x10);
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x44) = 0;
  *(undefined4 *)((int)param_1 + 0x48) = 0;
  *(undefined4 *)((int)param_1 + 0x4c) = 0;
  *(undefined4 *)((int)param_1 + 0x50) = 0;
  return (int)param_1;
}

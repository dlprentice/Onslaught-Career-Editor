/* address: 0x00450440 */
/* name: CFEPBEConfig__Unk_00450440 */
/* signature: void CFEPBEConfig__Unk_00450440(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFEPBEConfig__Unk_00450440(void)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;

  puVar2 = &DAT_006776f8;
  puVar3 = &DAT_009c6994;
  for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar3 = *puVar2;
    puVar2 = puVar2 + 1;
    puVar3 = puVar3 + 1;
  }
  DAT_009c73ea = 1;
  return;
}

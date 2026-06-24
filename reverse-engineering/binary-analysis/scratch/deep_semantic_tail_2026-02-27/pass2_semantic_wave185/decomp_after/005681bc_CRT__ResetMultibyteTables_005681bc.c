/* address: 0x005681bc */
/* name: CRT__ResetMultibyteTables_005681bc */
/* signature: void CRT__ResetMultibyteTables_005681bc(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__ResetMultibyteTables_005681bc(void)

{
  int iVar1;
  undefined4 *puVar2;

  puVar2 = &DAT_009d34c0;
  for (iVar1 = 0x40; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined1 *)puVar2 = 0;
  DAT_009d33a4 = 0;
  DAT_009d33bc = 0;
  DAT_009d35c4 = 0;
  DAT_009d33b0 = 0;
  DAT_009d33b4 = 0;
  DAT_009d33b8 = 0;
  return;
}

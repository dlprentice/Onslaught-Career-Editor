/* address: 0x0056c70a */
/* name: CRT__InitLocaleDefaults */
/* signature: void CRT__InitLocaleDefaults(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__InitLocaleDefaults(void)

{
  DAT_009d0b30._0_2_ = (ushort)DAT_009d0b30 | 0x104;
  DAT_009d0b34 = GetUserDefaultLCID();
  DAT_009d0b18 = DAT_009d0b34;
  return;
}

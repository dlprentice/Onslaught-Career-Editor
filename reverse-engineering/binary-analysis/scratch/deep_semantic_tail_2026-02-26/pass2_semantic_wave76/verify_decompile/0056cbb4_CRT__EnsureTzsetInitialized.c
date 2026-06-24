/* address: 0x0056cbb4 */
/* name: CRT__EnsureTzsetInitialized */
/* signature: void CRT__EnsureTzsetInitialized(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__EnsureTzsetInitialized(void)

{
  if (DAT_009d0bf8 == 0) {
    CDXTexture__Helper_00561179(0xb);
    if (DAT_009d0bf8 == 0) {
      CRT__Tzset();
      DAT_009d0bf8 = DAT_009d0bf8 + 1;
    }
    CTexture__Helper_005611da(0xb);
  }
  return;
}

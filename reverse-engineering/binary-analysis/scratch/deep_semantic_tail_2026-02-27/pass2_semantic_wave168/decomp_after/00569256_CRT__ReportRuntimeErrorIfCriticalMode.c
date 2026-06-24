/* address: 0x00569256 */
/* name: CRT__ReportRuntimeErrorIfCriticalMode */
/* signature: void CRT__ReportRuntimeErrorIfCriticalMode(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__ReportRuntimeErrorIfCriticalMode(void)

{
  if ((DAT_009d0914 == 1) || ((DAT_009d0914 == 0 && (DAT_00653644 == 1)))) {
    CRT__ReportRuntimeError(0xfc);
    if (DAT_009d0acc != (code *)0x0) {
      (*DAT_009d0acc)();
    }
    CRT__ReportRuntimeError(0xff);
  }
  return;
}

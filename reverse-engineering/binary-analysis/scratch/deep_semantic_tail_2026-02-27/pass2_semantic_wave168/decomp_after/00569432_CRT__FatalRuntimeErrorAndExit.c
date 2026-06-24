/* address: 0x00569432 */
/* name: CRT__FatalRuntimeErrorAndExit */
/* signature: void CRT__FatalRuntimeErrorAndExit(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__FatalRuntimeErrorAndExit(void)

{
  CRT__ReportRuntimeError(10);
  CDXTexture__Helper_0056d2e7(0x16);
                    /* WARNING: Subroutine does not return */
  __exit(3);
}

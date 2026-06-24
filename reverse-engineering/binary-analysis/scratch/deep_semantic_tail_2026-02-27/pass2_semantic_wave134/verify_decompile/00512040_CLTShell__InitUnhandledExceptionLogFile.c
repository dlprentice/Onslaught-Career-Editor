/* address: 0x00512040 */
/* name: CLTShell__InitUnhandledExceptionLogFile */
/* signature: int CLTShell__InitUnhandledExceptionLogFile(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CLTShell__InitUnhandledExceptionLogFile(void)

{
  SetUnhandledExceptionFilter((LPTOP_LEVEL_EXCEPTION_FILTER)0x0);
  fopen(s_OnslaughtException_txt_0063dc70,&DAT_0063dc88);
  return 1;
}

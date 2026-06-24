/* address: 0x0042d7a0 */
/* name: CController__ResetInactivityTimerConditional */
/* signature: void CController__ResetInactivityTimerConditional(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CController__ResetInactivityTimerConditional(void)

{
  if (DAT_0066e94c != '\0') {
    _DAT_0066e948 = 0.0;
    return;
  }
  _DAT_0066e948 = PLATFORM__GetSysTimeFloat();
  return;
}

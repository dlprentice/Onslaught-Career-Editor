/* address: 0x0042d7d0 */
/* name: CFrontEnd__SetLoadingTransitionGate */
/* signature: void __cdecl CFrontEnd__SetLoadingTransitionGate(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CFrontEnd__SetLoadingTransitionGate(int param_1)

{
  float fVar1;

  if (DAT_0066e94c != (char)param_1) {
    if (DAT_006630cc == 0) {
      fVar1 = PLATFORM__GetSysTimeFloat();
      _DAT_0066e948 = fVar1 - _DAT_0066e948;
    }
    DAT_0066e94c = (char)param_1;
  }
  return;
}

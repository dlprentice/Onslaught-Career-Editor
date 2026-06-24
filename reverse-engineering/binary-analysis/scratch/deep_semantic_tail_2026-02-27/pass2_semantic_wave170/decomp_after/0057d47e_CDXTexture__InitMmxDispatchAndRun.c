/* address: 0x0057d47e */
/* name: CDXTexture__InitMmxDispatchAndRun */
/* signature: void CDXTexture__InitMmxDispatchAndRun(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__InitMmxDispatchAndRun(void)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;

  iVar1 = CDXTexture__IsMmxEnabledBySystemConfig();
  if (iVar1 == 0) {
    PTR_CWaypointManager__InitMmxDispatchAndRun_00657974 = CWaypointManager__Helper_0057d0ee;
    UNRECOVERED_JUMPTABLE = CDXTexture__Downsample2x2Average32;
  }
  else {
    UNRECOVERED_JUMPTABLE = CWaypointManager__Helper_0057d32e;
    PTR_CWaypointManager__InitMmxDispatchAndRun_00657974 = CWaypointManager__Helper_0057d32e;
  }
  PTR_CDXTexture__InitMmxDispatchAndRun_00657978 = UNRECOVERED_JUMPTABLE;
                    /* WARNING: Could not recover jumptable at 0x0057d4ab. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}

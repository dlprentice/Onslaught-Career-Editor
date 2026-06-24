/* address: 0x0057d446 */
/* name: CWaypointManager__InitMmxDispatchAndRun */
/* signature: void CWaypointManager__InitMmxDispatchAndRun(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWaypointManager__InitMmxDispatchAndRun(void)

{
  int iVar1;

  iVar1 = CDXTexture__IsMmxEnabledBySystemConfig();
  if (iVar1 == 0) {
    PTR_CWaypointManager__InitMmxDispatchAndRun_00657974 = CWaypointManager__Helper_0057d0ee;
    PTR_CDXTexture__Helper_0057d47e_00657978 = CDXTexture__Downsample2x2Average32;
  }
  else {
    PTR_CWaypointManager__InitMmxDispatchAndRun_00657974 = CWaypointManager__Helper_0057d32e;
    PTR_CDXTexture__Helper_0057d47e_00657978 = CWaypointManager__Helper_0057d32e;
  }
                    /* WARNING: Could not recover jumptable at 0x0057d478. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_CWaypointManager__InitMmxDispatchAndRun_00657974)();
  return;
}

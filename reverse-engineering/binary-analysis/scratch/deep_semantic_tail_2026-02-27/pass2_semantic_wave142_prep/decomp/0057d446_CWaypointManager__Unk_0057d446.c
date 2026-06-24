/* address: 0x0057d446 */
/* name: CWaypointManager__Unk_0057d446 */
/* signature: void CWaypointManager__Unk_0057d446(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWaypointManager__Unk_0057d446(void)

{
  int iVar1;

  iVar1 = CDXTexture__IsMmxEnabledBySystemConfig();
  if (iVar1 == 0) {
    PTR_CWaypointManager__Unk_0057d446_00657974 = CWaypointManager__Helper_0057d0ee;
    PTR_CDXTexture__Helper_0057d47e_00657978 = CDXTexture__Downsample2x2Average32;
  }
  else {
    PTR_CWaypointManager__Unk_0057d446_00657974 = CWaypointManager__Helper_0057d32e;
    PTR_CDXTexture__Helper_0057d47e_00657978 = CWaypointManager__Helper_0057d32e;
  }
                    /* WARNING: Could not recover jumptable at 0x0057d478. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)PTR_CWaypointManager__Unk_0057d446_00657974)();
  return;
}

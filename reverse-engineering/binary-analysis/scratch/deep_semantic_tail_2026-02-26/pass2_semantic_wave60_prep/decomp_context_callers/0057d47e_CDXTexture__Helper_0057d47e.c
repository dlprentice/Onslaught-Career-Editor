/* address: 0x0057d47e */
/* name: CDXTexture__Helper_0057d47e */
/* signature: void CDXTexture__Helper_0057d47e(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Helper_0057d47e(void)

{
  int iVar1;
  code *UNRECOVERED_JUMPTABLE;

  iVar1 = CDXTexture__Unk_00589116();
  if (iVar1 == 0) {
    PTR_CWaypointManager__Unk_0057d446_00657974 = CWaypointManager__Helper_0057d0ee;
    UNRECOVERED_JUMPTABLE = CDXTexture__Unk_0057d244;
  }
  else {
    UNRECOVERED_JUMPTABLE = CWaypointManager__Helper_0057d32e;
    PTR_CWaypointManager__Unk_0057d446_00657974 = CWaypointManager__Helper_0057d32e;
  }
  PTR_CDXTexture__Helper_0057d47e_00657978 = UNRECOVERED_JUMPTABLE;
                    /* WARNING: Could not recover jumptable at 0x0057d4ab. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)();
  return;
}

/* address: 0x0056836a */
/* name: CRT__EnsureRuntimeInitSentinelSet */
/* signature: void CRT__EnsureRuntimeInitSentinelSet(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__EnsureRuntimeInitSentinelSet(void)

{
  if (DAT_009d4608 == 0) {
    CTexture__Helper_00567f92(-3);
    DAT_009d4608 = 1;
  }
  return;
}

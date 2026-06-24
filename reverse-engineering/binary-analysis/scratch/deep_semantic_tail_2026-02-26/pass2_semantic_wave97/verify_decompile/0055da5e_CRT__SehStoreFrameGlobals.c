/* address: 0x0055da5e */
/* name: CRT__SehStoreFrameGlobals */
/* signature: void CRT__SehStoreFrameGlobals(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__SehStoreFrameGlobals(void)

{
  undefined4 in_EAX;
  int unaff_EBP;

  DAT_006532d8 = *(undefined4 *)(unaff_EBP + 8);
  DAT_006532d4 = in_EAX;
  DAT_006532dc = unaff_EBP;
  return;
}

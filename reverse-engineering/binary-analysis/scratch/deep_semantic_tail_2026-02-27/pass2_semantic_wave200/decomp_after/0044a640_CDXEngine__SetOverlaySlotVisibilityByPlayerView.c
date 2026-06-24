/* address: 0x0044a640 */
/* name: CDXEngine__SetOverlaySlotVisibilityByPlayerView */
/* signature: void __stdcall CDXEngine__SetOverlaySlotVisibilityByPlayerView(int param_1) */


void CDXEngine__SetOverlaySlotVisibilityByPlayerView(int param_1)

{
  int in_ECX;
  int unaff_retaddr;

  CDXEngine__SetOverlaySlotsEnabledForActiveViews(*(void **)(in_ECX + 0x18),param_1,unaff_retaddr);
  return;
}

/* address: 0x004821e0 */
/* name: CDXCompass__ApplyRenderStateAdditive */
/* signature: void CDXCompass__ApplyRenderStateAdditive(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXCompass__ApplyRenderStateAdditive(void)

{
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  return;
}

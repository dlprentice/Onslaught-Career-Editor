/* address: 0x004821b0 */
/* name: CDXCompass__ApplyRenderStateModulate */
/* signature: void CDXCompass__ApplyRenderStateModulate(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXCompass__ApplyRenderStateModulate(void)

{
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,2);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  return;
}

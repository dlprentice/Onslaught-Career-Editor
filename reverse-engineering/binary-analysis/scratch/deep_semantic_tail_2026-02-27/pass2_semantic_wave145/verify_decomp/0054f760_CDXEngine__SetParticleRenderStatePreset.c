/* address: 0x0054f760 */
/* name: CDXEngine__SetParticleRenderStatePreset */
/* signature: void CDXEngine__SetParticleRenderStatePreset(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__SetParticleRenderStatePreset(void)

{
  RenderState_Set(0x13,2);
  RenderState_Set(0x14,1);
  D3DStateCache__SetSlotMode4or5(0);
  D3DStateCache__SetStateCached(0,5,2);
  D3DStateCache__SetStateCached(0,6,0);
  D3DStateCache__SetStateCached(0,4,4);
  RenderState_Set(0xe,1);
  RenderState_Set(0xf,1);
  return;
}

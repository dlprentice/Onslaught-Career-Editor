/* address: 0x00482090 */
/* name: CExplosionInitThing__Helper_00482090 */
/* signature: void CExplosionInitThing__Helper_00482090(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CExplosionInitThing__Helper_00482090(void)

{
  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  DAT_009c68ac = 0;
  DAT_009c690d = 1;
  DAT_009c68ad = 0;
  DAT_009c6910 = 1;
  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
  D3DStateCache__SetMipFilterPoint(0);
  D3DStateCache__SetState114Raw(0,6,2);
  D3DStateCache__SetState114Raw(0,5,2);
  RenderState_Set(0x17,4);
  D3DStateCache__SetStateCached(0,2,2);
  D3DStateCache__SetStateCached(0,3,0);
  D3DStateCache__SetStateCached(0,1,4);
  RenderState_Set(0xf,1);
  RenderState_Set(0x18,8);
  RenderState_Set(0x1b,1);
  RenderState_Set(0xe,0);
  RenderState_Set(7,0);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  return;
}

/* address: 0x0044d210 */
/* name: CUnitAI__RenderWithStaticShadowVisibilityUpdate */
/* signature: void __thiscall CUnitAI__RenderWithStaticShadowVisibilityUpdate(void * this, int param_1, int param_2) */


void __thiscall CUnitAI__RenderWithStaticShadowVisibilityUpdate(void *this,int param_1,int param_2)

{
  uint unaff_ESI;

  CStaticShadows__UpdateVisibility(this,0);
  CThing__Render(this,param_1,unaff_ESI);
  return;
}

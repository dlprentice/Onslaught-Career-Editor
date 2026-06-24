/* address: 0x0044a2c0 */
/* name: CResourceAccumulator__ReloadWaterRenderTextures */
/* signature: void __fastcall CResourceAccumulator__ReloadWaterRenderTextures(int param_1, void * param_2) */


void __fastcall CResourceAccumulator__ReloadWaterRenderTextures(int param_1,void *param_2)

{
  CWaterRenderSystem__ReloadTextures(*(void **)(param_1 + 0x14),param_2);
  return;
}

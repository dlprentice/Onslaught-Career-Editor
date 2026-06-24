/* address: 0x0048dec0 */
/* name: CResourceAccumulator__Helper_0048dec0 */
/* signature: void CResourceAccumulator__Helper_0048dec0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CResourceAccumulator__Helper_0048dec0(void)

{
  char local_18 [24];

  sprintf(local_18,s_mixers_detail__2d_tga_0062d80c);
  if (DAT_00662dd4 != 0) {
    DAT_0067a7d0 = CTexture__FindTexture(local_18,5,0,-1,1,1);
    return;
  }
  DAT_0067a7d0 = CTexture__FindTexture(local_18,0,0,-1,1,1);
  return;
}

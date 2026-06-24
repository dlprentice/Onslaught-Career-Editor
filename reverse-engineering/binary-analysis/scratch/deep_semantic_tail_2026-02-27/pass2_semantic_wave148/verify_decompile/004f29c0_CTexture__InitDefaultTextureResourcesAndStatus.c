/* address: 0x004f29c0 */
/* name: CTexture__InitDefaultTextureResourcesAndStatus */
/* signature: void CTexture__InitDefaultTextureResourcesAndStatus(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CTexture__InitDefaultTextureResourcesAndStatus(void)

{
  char local_100 [256];

  if (DAT_0083d9b4 == (int *)0x0) {
    DAT_0083d9b4 = CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1);
  }
  sprintf(local_100,s_Loading_texture_resources_00632f78);
  CConsole__Status(&DAT_00663498,local_100);
  CConsole__StatusDone(&DAT_00663498,local_100,'\x01');
  return;
}

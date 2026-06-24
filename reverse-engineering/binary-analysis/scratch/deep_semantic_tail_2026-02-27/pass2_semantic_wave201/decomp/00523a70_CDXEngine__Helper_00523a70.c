/* address: 0x00523a70 */
/* name: CDXEngine__Helper_00523a70 */
/* signature: void CDXEngine__Helper_00523a70(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__Helper_00523a70(void)

{
  if (DAT_0089bd98 == (int *)0x0) {
    DAT_0089bd98 = CTexture__FindTexture(s_mouse_tga_00640058,0,0,-1,1,1);
    if (DAT_0089bd98 == (int *)0x0) {
      if (DAT_0089ce84 == (int *)0x0) {
        DAT_0089ce84 = CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1);
      }
      DAT_0089bd98 = DAT_0089ce84;
      DAT_0089ce84[0x29] = DAT_0089ce84[0x29] + 1;
    }
  }
  CVBufTexture__DrawSpriteEx
            ((float)DAT_0089bda8,(float)DAT_0089bda4,0.001,DAT_0089bd98,0,0,1.0,0.0,
             (float)(DAT_00640054 << 0x18 | 0xffffff),0.25,0.25,0.0,0.96875,0.0,0.96875);
  return;
}

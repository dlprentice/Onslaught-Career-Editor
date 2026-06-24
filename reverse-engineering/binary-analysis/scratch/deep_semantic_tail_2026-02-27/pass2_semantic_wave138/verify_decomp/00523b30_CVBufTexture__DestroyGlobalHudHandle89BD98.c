/* address: 0x00523b30 */
/* name: CVBufTexture__DestroyGlobalHudHandle89BD98 */
/* signature: void CVBufTexture__DestroyGlobalHudHandle89BD98(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CVBufTexture__DestroyGlobalHudHandle89BD98(void)

{
  if (DAT_0089bd98 != 0) {
    CHud__Helper_004f27e0(DAT_0089bd98 + 8);
    DAT_0089bd98 = 0;
  }
  return;
}

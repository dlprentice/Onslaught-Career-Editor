/* address: 0x005285b0 */
/* name: PCPlatform__ResetAsyncMusicStream */
/* signature: void PCPlatform__ResetAsyncMusicStream(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void PCPlatform__ResetAsyncMusicStream(void)

{
  if (DAT_0089bec8 != (int *)0x0) {
    (**(code **)(*DAT_0089bec8 + 0x48))(DAT_0089bec8);
    ResetEvent(DAT_0089bec4);
    ResetEvent(DAT_0089bec0);
    ResetEvent(PCPlatform__KickAsyncMusicStreamRead);
  }
  return;
}

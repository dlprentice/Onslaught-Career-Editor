/* address: 0x004cddf0 */
/* name: CEngine__RestoreAudioAfterDeviceReset */
/* signature: void __cdecl CEngine__RestoreAudioAfterDeviceReset(int param_1) */


void __cdecl CEngine__RestoreAudioAfterDeviceReset(int param_1)

{
  CSoundManager__ReinitializeAfterDeviceLoss();
  if ((char)param_1 != '\0') {
    if (DAT_00662dcc != 0) {
      CMusic__PlayTrackByType(&DAT_00889a48,0,0);
    }
    return;
  }
  CGame__PlayMusicForCurrentLevel(&DAT_008a9a98);
  return;
}

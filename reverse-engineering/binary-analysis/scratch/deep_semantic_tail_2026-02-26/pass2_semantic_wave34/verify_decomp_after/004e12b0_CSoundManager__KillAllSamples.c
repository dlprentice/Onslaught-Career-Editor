/* address: 0x004e12b0 */
/* name: CSoundManager__KillAllSamples */
/* signature: void __fastcall CSoundManager__KillAllSamples(int param_1) */


void __fastcall CSoundManager__KillAllSamples(int param_1)

{
  int *sound_event;

  for (sound_event = *(int **)(param_1 + 0xc); sound_event != (int *)0x0;
      sound_event = (int *)sound_event[0x1d]) {
    if ((sound_event[0x1f] == 1) && ((int *)*sound_event != (int *)0x0)) {
      (**(code **)(*(int *)*sound_event + 0x18))(sound_event);
    }
    if (-1 < sound_event[1]) {
      CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event);
    }
    *(undefined1 *)(sound_event + 2) = 0;
    CGenericActiveReader__SetReader(sound_event,(void *)0x0);
  }
  return;
}

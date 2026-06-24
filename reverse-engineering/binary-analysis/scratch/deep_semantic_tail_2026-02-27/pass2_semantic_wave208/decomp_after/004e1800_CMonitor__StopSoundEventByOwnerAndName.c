/* address: 0x004e1800 */
/* name: CMonitor__StopSoundEventByOwnerAndName */
/* signature: void __thiscall CMonitor__StopSoundEventByOwnerAndName(void * this, int param_1, void * param_2, int param_3) */


void __thiscall
CMonitor__StopSoundEventByOwnerAndName(void *this,int param_1,void *param_2,int param_3)

{
  int *sound_event;
  int iVar1;

  if (*(char *)((int)this + 4) != '\0') {
    for (sound_event = *(int **)((int)this + 0xc); sound_event != (int *)0x0;
        sound_event = (int *)sound_event[0x1d]) {
      if ((((char)sound_event[2] != '\0') && ((void *)*sound_event == param_2)) &&
         (iVar1 = stricmp((char *)(sound_event[3] + 8),(char *)param_1), iVar1 == 0)) {
        if ((sound_event[0x1f] == 1) && ((int *)*sound_event != (int *)0x0)) {
          (**(code **)(*(int *)*sound_event + 0x18))(sound_event);
        }
        if (-1 < sound_event[1]) {
          CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event);
        }
        *(undefined1 *)(sound_event + 2) = 0;
        CGenericActiveReader__SetReader(sound_event,(void *)0x0);
      }
    }
  }
  return;
}

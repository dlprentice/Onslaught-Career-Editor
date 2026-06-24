/* address: 0x004e1130 */
/* name: CSoundManager__Unk_004e1130 */
/* signature: void __thiscall CSoundManager__Unk_004e1130(void * this, int param_1, void * param_2) */


void __thiscall CSoundManager__Unk_004e1130(void *this,int param_1,void *param_2)

{
  int *sound_event;
  int *piVar1;

  for (sound_event = *(int **)((int)this + 0xc); sound_event != (int *)0x0;
      sound_event = (int *)sound_event[0x1d]) {
    piVar1 = (int *)*sound_event;
    if ((piVar1 == (int *)param_1) && ((char)sound_event[2] != '\0')) {
      if ((sound_event[0x1f] == 1) && (piVar1 != (int *)0x0)) {
        (**(code **)(*piVar1 + 0x18))(sound_event);
      }
      if (-1 < sound_event[1]) {
        CSoundManager__StopAndReleaseChannel(&DAT_00896988,sound_event);
      }
      *(undefined1 *)(sound_event + 2) = 0;
      CGenericActiveReader__SetReader(sound_event,(void *)0x0);
    }
  }
  return;
}

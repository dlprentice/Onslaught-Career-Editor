/* address: 0x004e1300 */
/* name: CSoundManager__Unk_004e1300 */
/* signature: void __fastcall CSoundManager__Unk_004e1300(int param_1) */


void __fastcall CSoundManager__Unk_004e1300(int param_1)

{
  void *sound_event;

  for (sound_event = *(void **)(param_1 + 0xc); sound_event != (void *)0x0;
      sound_event = *(void **)((int)sound_event + 0x74)) {
    if (*(int *)((int)sound_event + 4) != -1) {
      CSoundManager__StopChannel(&DAT_00896988,sound_event);
    }
    *(undefined4 *)((int)sound_event + 0x84) = 1;
  }
  return;
}

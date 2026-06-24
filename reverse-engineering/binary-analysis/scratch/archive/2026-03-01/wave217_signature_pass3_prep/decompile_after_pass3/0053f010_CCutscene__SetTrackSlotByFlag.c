/* address: 0x0053f010 */
/* name: CCutscene__SetTrackSlotByFlag */
/* signature: void __thiscall CCutscene__SetTrackSlotByFlag(void * this, int track_slot, int track_flag, int track_value) */


void __thiscall
CCutscene__SetTrackSlotByFlag(void *this,int track_slot,int track_flag,int track_value)

{
  if ((char)track_flag != '\0') {
    *(int *)((int)this + 0x4cc) = track_slot;
    return;
  }
  *(int *)((int)this + 0x4d0) = track_slot;
  return;
}

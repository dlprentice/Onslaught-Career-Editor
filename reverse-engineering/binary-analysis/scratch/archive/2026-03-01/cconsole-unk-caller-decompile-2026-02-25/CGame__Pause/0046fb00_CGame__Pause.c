/* address: 0x0046fb00 */
/* name: CGame__Pause */
/* signature: void __thiscall CGame__Pause(void * this, int toggle_pause_menu, void * from_controller) */


/* Source-aligned with CGame::Pause(BOOL toggle_pause_menu, CController* from_controller). If
   gameplay state allows and game is not already paused: sets pause flag, disables vibration for
   active controllers, and optionally activates pause-menu control handoff via from_controller. */

void __thiscall CGame__Pause(void *this,int toggle_pause_menu,void *from_controller)

{
  int unaff_ESI;
  float fVar1;
  int unaff_EDI;
  undefined4 *puVar2;

  if (1 < DAT_008a9ac0) {
    CFastVB__Unk_0055e183(0x62c1f8);
    if (*(int *)((int)this + 0x2c) == 0) {
      *(undefined4 *)((int)this + 0x2c) = 1;
      fVar1 = 0.0;
      puVar2 = (undefined4 *)((int)this + 0x2b4);
      do {
        if ((void *)*puVar2 != (void *)0x0) {
          CUnitAI__Unk_0042e750((void *)*puVar2,(void *)0x0,fVar1,unaff_EDI);
        }
        fVar1 = (float)((int)fVar1 + 1);
        puVar2 = puVar2 + 1;
      } while ((int)fVar1 < 4);
      if ((toggle_pause_menu != 0) && (from_controller != (void *)0x0)) {
        CPauseMenu__Unk_004d0ff0(*(void **)((int)this + 0x2f4),1,unaff_ESI);
        CConsole__Unk_0042d3b0();
        CController__SetToControl(from_controller,*(void **)((int)this + 0x2f4));
      }
    }
  }
  return;
}
